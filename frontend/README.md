# Living Cap Table frontend

A small, dependency-light page for the live deployment at
`0x2B20c02d514478a1E1E687628e12c86e100A5Ca1` on GenLayer's Studio Network.
Vite + vanilla TypeScript, no framework - the app is one file
([`src/main.ts`](src/main.ts)) because there wasn't enough surface area here
to justify one.

## What it does

- Loads the rubric and cap table straight from the live contract on page
  load, with no wallet required - anyone can read it.
- "Connect wallet" (any injected wallet, e.g. MetaMask) lets a visitor
  register themselves as a contributor and call `recompute_equity()` for
  real, from their own wallet, sending an actual transaction to the live
  contract.
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
(chain id `61999`, RPC `https://studio.genlayer.com/api`) - the app calls
`client.connect("studionet")` on connect, which prompts the wallet to add or
switch to it if it isn't already configured.

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
