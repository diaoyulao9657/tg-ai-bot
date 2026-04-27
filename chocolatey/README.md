# TokenMix CLI — Chocolatey Package

Chocolatey package definition for installing the [TokenMix](https://tokenmix.ai) CLI on Windows.

## Install

    choco install tokenmix-cli

## How it works

This package depends on `rust-ms` (Rust on Windows) and runs `cargo install tokenmix-cli` at install time, fetching from [crates.io](https://crates.io/crates/tokenmix-cli).

## License

MIT
