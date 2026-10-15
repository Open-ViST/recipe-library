// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OpenViST contributors
use std::env;
use std::fs::File;
use std::io::{self, Read};
use std::process;

fn run() -> Result<(), String> {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.len() != 1 {
        return Err("usage: ./recipe <file-path|->".to_string());
    }

    let mut bytes = Vec::new();
    if args[0] == "-" {
        io::stdin()
            .read_to_end(&mut bytes)
            .map_err(|e| format!("could not read standard input: {e}"))?;
    } else {
        File::open(&args[0])
            .map_err(|e| format!("could not open '{}': {e}", args[0]))?
            .read_to_end(&mut bytes)
            .map_err(|e| format!("could not read '{}': {e}", args[0]))?;
    }

    let text = std::str::from_utf8(&bytes)
        .map_err(|e| format!("input is not valid UTF-8: {e}"))?;

    let mut tab_count = 0usize;
    let mut affected_lines = Vec::new();
    for (index, line) in text.split('\n').enumerate() {
        let count = line.chars().filter(|&ch| ch == '\t').count();
        tab_count += count;
        if count > 0 {
            affected_lines.push(index + 1);
        }
    }

    println!("tabs: {tab_count}");
    println!("lines_with_tabs: {}", affected_lines.len());
    if affected_lines.is_empty() {
        println!("line_numbers: none");
    } else {
        let numbers = affected_lines
            .iter()
            .map(usize::to_string)
            .collect::<Vec<_>>()
            .join(",");
        println!("line_numbers: {numbers}");
    }
    Ok(())
}

fn main() {
    if let Err(message) = run() {
        eprintln!("error: {message}");
        process::exit(2);
    }
}
