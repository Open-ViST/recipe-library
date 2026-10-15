// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OpenViST contributors
use std::env;
use std::fs::File;
use std::io::{self, Read};
use std::process;

fn run() -> Result<(), String> {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.len() != 1 {
        return Err("usage: recipe <file|->".to_string());
    }

    let mut bytes = Vec::new();
    if args[0] == "-" {
        io::stdin()
            .lock()
            .read_to_end(&mut bytes)
            .map_err(|e| format!("cannot read standard input: {e}"))?;
    } else {
        File::open(&args[0])
            .map_err(|e| format!("cannot open '{}': {e}", args[0]))?
            .read_to_end(&mut bytes)
            .map_err(|e| format!("cannot read '{}': {e}", args[0]))?;
    }

    std::str::from_utf8(&bytes)
        .map_err(|e| format!("input is not valid UTF-8: {e}"))?;

    let has_bom = bytes.starts_with(&[0xEF, 0xBB, 0xBF]);
    println!("bytes: {}", bytes.len());
    println!("utf8_bom: {}", if has_bom { "yes" } else { "no" });
    Ok(())
}

fn main() {
    if let Err(message) = run() {
        eprintln!("error: {message}");
        eprintln!("hint: provide one UTF-8 file path or - to read standard input");
        process::exit(2);
    }
}
