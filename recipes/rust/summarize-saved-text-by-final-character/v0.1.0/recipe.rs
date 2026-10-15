// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OpenViST contributors
use std::collections::BTreeMap;
use std::env;
use std::fs::File;
use std::io::{self, BufRead, BufReader};
use std::process;

fn run() -> Result<(), String> {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.len() != 1 {
        return Err("Usage: recipe <UTF-8-file|->".to_string());
    }

    let reader: Box<dyn BufRead> = if args[0] == "-" {
        Box::new(BufReader::new(io::stdin().lock()))
    } else {
        let file = File::open(&args[0])
            .map_err(|e| format!("cannot open '{}': {e}", args[0]))?;
        Box::new(BufReader::new(file))
    };

    let mut counts: BTreeMap<char, usize> = BTreeMap::new();
    let mut total = 0usize;
    for (index, result) in reader.lines().enumerate() {
        let line = result.map_err(|e| format!("cannot read line {} as UTF-8: {e}", index + 1))?;
        if let Some(ch) = line.trim().chars().last() {
            total += 1;
            *counts.entry(ch).or_insert(0) += 1;
        }
    }

    println!("nonblank_lines: {total}");
    for (ch, count) in counts {
        println!("{}: {count}", ch.escape_default());
    }
    Ok(())
}

fn main() {
    if let Err(message) = run() {
        eprintln!("error: {message}");
        process::exit(2);
    }
}
