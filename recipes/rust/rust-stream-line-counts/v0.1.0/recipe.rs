// Copyright (c) 2014 Jorge Aparicio
// 
// Permission is hereby granted, free of charge, to any
// person obtaining a copy of this software and associated
// documentation files (the "Software"), to deal in the
// Software without restriction, including without
// limitation the rights to use, copy, modify, merge,
// publish, distribute, sublicense, and/or sell copies of
// the Software, and to permit persons to whom the Software
// is furnished to do so, subject to the following
// conditions:
// 
// The above copyright notice and this permission notice
// shall be included in all copies or substantial portions
// of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
// ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
// TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
// PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
// SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
// CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
// OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
// IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
// DEALINGS IN THE SOFTWARE.
// 
// Adapted by OpenViST; see what_changed and upstream blob SHA.
// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OpenViST contributors
// Adapted from Rust by Example, “Read Lines” (MIT; Copyright (c) 2014 Jorge Aparicio).
// Improvements: accepts a file path or stdin, counts lines without collecting them,
// classifies Unicode-whitespace-only lines, and propagates read/UTF-8 errors.
use std::env;
use std::fs::File;
use std::io::{self, BufRead, BufReader};

fn count_lines<R: BufRead>(reader: R) -> io::Result<(u64, u64, u64)> {
    let mut total = 0_u64;
    let mut blank = 0_u64;
    let mut nonblank = 0_u64;

    for line_result in reader.lines() {
        let line = line_result?;
        total += 1;
        if line.chars().all(char::is_whitespace) {
            blank += 1;
        } else {
            nonblank += 1;
        }
    }

    Ok((total, blank, nonblank))
}

fn run() -> Result<(), String> {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.len() != 1 {
        return Err("usage: recipe <UTF-8-file|->".to_string());
    }

    let counts = if args[0] == "-" {
        let stdin = io::stdin();
        count_lines(stdin.lock()).map_err(|e| format!("failed to read standard input: {e}"))?
    } else {
        let file = File::open(&args[0])
            .map_err(|e| format!("failed to open '{}': {e}", args[0]))?;
        count_lines(BufReader::new(file))
            .map_err(|e| format!("failed to read '{}': {e}", args[0]))?
    };

    println!("total: {}", counts.0);
    println!("blank: {}", counts.1);
    println!("nonblank: {}", counts.2);
    Ok(())
}

fn main() {
    if let Err(message) = run() {
        eprintln!("error: {message}");
        std::process::exit(2);
    }
}

// Build with the intended runner, Rust 1.90.0, edition 2021:
// rustc --edition=2021 recipe.rs -o recipe
// Usage: ./recipe <UTF-8-file|->