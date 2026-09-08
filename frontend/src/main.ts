import { createClient, buildGenVmPositionalArgs } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

type GenLayerClient = ReturnType<typeof createClient>;
type ContractSchema = Awaited<ReturnType<GenLayerClient["getContractSchema"]>>;

// The real, live Living Cap Table deployment. See ../README.md "Live deployment".
const CONTRACT_ADDRESS = "0x2B20c02d514478a1E1E687628e12c86e100A5Ca1" as `0x${string}`;
const EXPLORER_URL = "https://genlayer-explorer.vercel.app";

type EthereumProvider = {
  request: (args: { method: string; params?: unknown[] }) => Promise<unknown>;
  on?: (event: string, handler: (...args: unknown[]) => void) => void;
};

declare global {
  interface Window {
    ethereum?: EthereumProvider;
  }
}

interface ContributorRow {
  github_handle: string;
  wallet: string;
  score: number;
  equity_bps: number;
  last_scored_reason: string;
}

type CapTable = Record<string, ContributorRow>;

interface AppState {
  rubric: string;
  capTable: CapTable;
  connectedAddress: string | null;
  schema: ContractSchema | null;
  status: { kind: "idle" | "pending" | "ok" | "error"; message: string };
  busy: boolean;
}

const state: AppState = {
  rubric: "",
  capTable: {},
  connectedAddress: null,
  schema: null,
  status: { kind: "idle", message: "" },
  busy: false,
};

// No wallet needed to read - anyone can see the live cap table.
const readClient = createClient({ chain: studionet });

let writeClient: GenLayerClient | null = null;

async function loadCapTable(): Promise<void> {
  const [rubric, capTable] = await Promise.all([
    readClient.readContract({
      address: CONTRACT_ADDRESS,
      functionName: "get_rubric",
      args: [],
      jsonSafeReturn: true,
    }),
    readClient.readContract({
      address: CONTRACT_ADDRESS,
      functionName: "get_cap_table",
      args: [],
      jsonSafeReturn: true,
    }),
  ]);
  state.rubric = String(rubric ?? "");
  state.capTable = (capTable as unknown as CapTable) ?? {};
  render();
}

async function connectWallet(): Promise<void> {
  if (!window.ethereum) {
    setStatus("error", "No wallet found. Install MetaMask or another injected wallet.");
    return;
  }
  try {
    const accounts = (await window.ethereum.request({
      method: "eth_requestAccounts",
    })) as string[];
    const address = accounts[0];
    if (!address) throw new Error("No account returned by wallet.");

    writeClient = createClient({
      chain: studionet,
      account: address as `0x${string}`,
      provider: window.ethereum,
    });

    // Prompts the wallet to add/switch to the Studio Network if it isn't
    // already on it. Non-fatal if the wallet rejects or already matches.
    try {
      await writeClient.connect("studionet");
    } catch (err) {
      console.warn("Network switch prompt was not completed:", err);
    }

    state.connectedAddress = address;
    setStatus("idle", "");
    render();
  } catch (err) {
    setStatus("error", messageOf(err));
  }
}

async function getSchema(): Promise<ContractSchema> {
  if (!state.schema) {
    state.schema = await readClient.getContractSchema(CONTRACT_ADDRESS);
  }
  return state.schema;
}

async function registerContributor(handle: string, githubHandle: string): Promise<void> {
  if (!writeClient || !state.connectedAddress) {
    setStatus("error", "Connect your wallet first.");
    return;
  }
  setBusy(true, "Sending register_contributor...");
  try {
    const schema = await getSchema();
    const args = buildGenVmPositionalArgs({
      schema,
      functionName: "register_contributor",
      valuesByParamName: {
        handle,
        github_handle: githubHandle,
        wallet: state.connectedAddress,
      },
    });
    const hash = await writeClient.writeContract({
      address: CONTRACT_ADDRESS,
      functionName: "register_contributor",
      args: args as any[],
      value: 0n,
    });
    setStatus("pending", `Submitted: ${hash}`);
    await readClient.waitForTransactionReceipt({ hash: hash as any, status: "ACCEPTED" as any });
    await loadCapTable();
    setStatus("ok", `Registered. Tx: ${hash}`);
  } catch (err) {
    setStatus("error", messageOf(err));
  } finally {
    setBusy(false);
  }
}

async function recomputeEquity(): Promise<void> {
  if (!writeClient) {
    setStatus("error", "Connect your wallet first.");
    return;
  }
  setBusy(true, "Sending recompute_equity - validators are pulling real GitHub activity, this can take a moment...");
  try {
    const hash = await writeClient.writeContract({
      address: CONTRACT_ADDRESS,
      functionName: "recompute_equity",
      args: [],
      value: 0n,
    });
    setStatus("pending", `Submitted: ${hash}`);
    await readClient.waitForTransactionReceipt({ hash: hash as any, status: "ACCEPTED" as any });
    await loadCapTable();
    setStatus("ok", `Recomputed. Tx: ${hash}`);
  } catch (err) {
    setStatus("error", messageOf(err));
  } finally {
    setBusy(false);
  }
}

function setStatus(kind: AppState["status"]["kind"], message: string): void {
  state.status = { kind, message };
  render();
}

function setBusy(busy: boolean, message?: string): void {
  state.busy = busy;
  if (message) state.status = { kind: "pending", message };
  render();
}

function messageOf(err: unknown): string {
  if (err instanceof Error) return err.message;
  return String(err);
}

function shortAddress(addr: string): string {
  return addr.length > 12 ? `${addr.slice(0, 6)}...${addr.slice(-4)}` : addr;
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderCapTable(): string {
  const handles = Object.keys(state.capTable);
  if (handles.length === 0) {
    return `<p class="empty">No contributors registered yet.</p>`;
  }
  return handles
    .map((handle) => {
      const c = state.capTable[handle];
      const pct = (c.equity_bps / 100).toFixed(2);
      return `
        <div class="contributor">
          <div class="contributor-head">
            <span class="contributor-handle">${escapeHtml(handle)}</span>
            <span class="contributor-pct">${pct}%</span>
          </div>
          <div class="contributor-meta">
            github.com/${escapeHtml(c.github_handle)} &middot; score ${c.score} &middot; ${shortAddress(c.wallet)}
          </div>
          ${c.last_scored_reason ? `<div class="contributor-reason">${escapeHtml(c.last_scored_reason)}</div>` : ""}
        </div>
      `;
    })
    .join("");
}

function render(): void {
  const app = document.getElementById("app");
  if (!app) return;

  app.innerHTML = `
    <a class="back-link" href="/">&larr; What is this?</a>
    <header>
      <h1>The Living Cap Table</h1>
      <p class="tagline">Equity that's read, not negotiated.</p>
    </header>
    <div class="address-row">
      <span>Contract:</span>
      <span>${CONTRACT_ADDRESS}</span>
      <a href="${EXPLORER_URL}" target="_blank" rel="noreferrer">Explorer</a>
      <span>&middot; Studio Network</span>
    </div>

    <div class="card">
      <h2>Rubric</h2>
      <p class="rubric-text">${state.rubric ? escapeHtml(state.rubric) : "<span class=\"empty\">Not loaded yet.</span>"}</p>
    </div>

    <div class="card">
      <h2>Cap table</h2>
      ${renderCapTable()}
    </div>

    <div class="card">
      <h2>Wallet</h2>
      <div class="wallet-row">
        ${
          state.connectedAddress
            ? `<span>Connected as ${shortAddress(state.connectedAddress)}</span>`
            : `<button id="connect-btn" class="primary">Connect wallet</button>`
        }
      </div>
    </div>

    <div class="card">
      <h2>Register as a contributor</h2>
      <form id="register-form" class="register-form">
        <input name="handle" placeholder="Handle (e.g. your name in this venture)" required />
        <input name="github_handle" placeholder="GitHub username" required />
        <button type="submit" ${state.connectedAddress ? "" : "disabled"}>
          Register with connected wallet
        </button>
      </form>
    </div>

    <div class="card">
      <h2>Recompute equity</h2>
      <p class="contributor-meta">
        Validators pull every registered contributor's real public GitHub activity
        and re-score it against the rubric above. Anyone with a connected wallet
        can trigger this - it's not restricted to the founder.
      </p>
      <div class="actions-row">
        <button id="recompute-btn" class="primary" ${state.connectedAddress && !state.busy ? "" : "disabled"}>
          Recompute equity
        </button>
      </div>
      ${state.status.message ? `<p class="status ${state.status.kind}">${escapeHtml(state.status.message)}</p>` : ""}
    </div>
  `;

  document.getElementById("connect-btn")?.addEventListener("click", () => {
    void connectWallet();
  });

  document.getElementById("recompute-btn")?.addEventListener("click", () => {
    void recomputeEquity();
  });

  const form = document.getElementById("register-form") as HTMLFormElement | null;
  form?.addEventListener("submit", (e) => {
    e.preventDefault();
    const data = new FormData(form);
    const handle = String(data.get("handle") ?? "").trim();
    const githubHandle = String(data.get("github_handle") ?? "").trim();
    if (!handle || !githubHandle) return;
    void registerContributor(handle, githubHandle);
    form.reset();
  });
}

render();
void loadCapTable().catch((err) => setStatus("error", messageOf(err)));
