# Living Cap Table frontend

**Live: https://living-cap-table-angelraphs-projects.vercel.app**

A small, dependency-light site for the live deployment at
`0x2B20c02d514478a1E1E687628e12c86e100A5Ca1` on GenLayer's Studio Network.
Vite + vanilla TypeScript, no framework.

Two pages:

- **`index.html`** - a plain-English explainer. What the problem is (told as
  a one-paragraph story, not a pitch), how the mechanism works in four
  steps, why the number can be trusted. No jargon needed to follow it.
- **`app.html`** ([`src/main.ts`](src/main.ts)) - the actual dashboard.
  Real rubric, real cap table, connect-a-wallet-and-trigger-it-for-real.

Styled against GenLayer's own design system
([genlayer-foundation/genlayer-design](https://github.com/genlayer-foundation/genlayer-design)),
not a guess at it: Kinetic Cobalt (`#110FFF`) as the one strong accent,
Carbon Void dark surfaces by default, Space Grotesk for headings and
Switzer for body text, pill-shaped buttons, and the signature pink-to-blue
gradient used sparingly as a soft, slow-drifting bloom behind the opening
hero. Real hex values and font names pulled directly from that repo's
`colors_and_type.css`, not copied from a secondhand summary.

## What the dashboard does

- Loads the rubric and cap table straight from the live contract on page
  load, with no wallet required - anyone can read it.
- "Connect wallet" shows a picker of every wallet extension actually
  installed in the visitor's browser (via EIP-6963 discovery, not just
  whichever one happened to grab `window.ethereum`), and lets them register
  as a contributor or call `recompute_equity()` for real, from their own
  wallet, sending an actual transaction to the live contract. A connected
  wallet can be disconnected again from the same panel.
- Uses `genlayer-js`'s `buildGenVmPositionalArgs()` to turn plain form values
  into correctly-typed calldata against the contract's real on-chain schema
  (fetched via `getContractSchema`) - this matters specifically for the
  `wallet` argument, which needs to be encoded as an address, not a string.

## Running it

```bash
npm install
npm run dev
```

Opens on `http://localhost:5173`. The read side (rubric, cap table) works
immediately with no setup. The write side (register, recompute) needs a
browser wallet extension pointed at the GenLayer Studio Network
(chain id `61999`, RPC `https://studio.genlayer.com/api`).

```bash
npm run build   # type-checks with tsc -b, then builds to dist/
```

## Verified so far

The read path has been run for real against the live contract: rubric and
cap table both load correctly with no console errors, showing the actual
on-chain values.

The write path has also been clicked through for real, with an actual
browser wallet: connect, `recompute_equity()`, transaction lands, cap table
updates with a fresh judgment. See the top-level README's "Live deployment"
section for that result.

One real bug found this way: picking a non-MetaMask wallet (OKX, tested)
from the picker would still sometimes pop up MetaMask on top of it. Traced
to `genlayer-js`'s `client.connect()` in this SDK version - despite the
name, it isn't a generic network-switch call, it's specifically MetaMask's
Snap-installation flow, and it's hardcoded to talk to `window.ethereum`
regardless of which provider the client was actually configured with. It
only visibly interrupted when it had something to do (add/switch the
chain, or install the Snap), which is why it looked intermittent - silent
when MetaMask already happened to be in the right state, a surprise
popup when it didn't. Removed the call entirely: GenLayer's Studio Network
chains skip the wallet-network-match check outright, and every write
already correctly goes through whichever provider was actually picked.
