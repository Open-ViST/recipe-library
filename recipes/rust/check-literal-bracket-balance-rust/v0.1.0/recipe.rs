use std::io::{self, Read, Write};

fn invalid() -> ! {
    let stderr = io::stderr();
    let mut err = stderr.lock();
    let _ = err.write_all(b"error: invalid input\n");
    let _ = err.flush();
    std::process::exit(2);
}

fn balanced(line: &str) -> bool {
    let mut stack: Vec<char> = Vec::new();
    for ch in line.chars() {
        match ch {
            '(' | '[' | '{' => stack.push(ch),
            ')' | ']' | '}' => {
                let expected = match ch {
                    ')' => '(',
                    ']' => '[',
                    '}' => '{',
                    _ => unreachable!(),
                };
                if stack.pop() != Some(expected) {
                    return false;
                }
            }
            _ => {}
        }
    }
    stack.is_empty()
}

fn main() {
    if std::env::args_os().skip(1).next().is_some() {
        invalid();
    }

    let mut input = Vec::new();
    {
        let stdin = io::stdin();
        let mut reader = stdin.lock().take(65_537);
        if reader.read_to_end(&mut input).is_err() {
            invalid();
        }
    }
    if input.len() > 65_536 {
        invalid();
    }

    let text = match std::str::from_utf8(&input) {
        Ok(text) => text,
        Err(_) => invalid(),
    };
    if text.starts_with('\u{feff}') || text.contains('\r') {
        invalid();
    }

    // Validate every retained line before classifying any line.
    let mut lines: Vec<&str> = Vec::new();
    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        if line.len() > 256 || lines.len() >= 100 {
            invalid();
        }
        lines.push(line);
    }

    let mut output = String::from("{\"balanced\":[");
    for (index, line) in lines.iter().enumerate() {
        if index != 0 {
            output.push(',');
        }
        output.push_str(if balanced(line) { "true" } else { "false" });
    }
    output.push_str("]}\n");

    let stdout = io::stdout();
    let mut out = stdout.lock();
    if out.write_all(output.as_bytes()).is_err() || out.flush().is_err() {
        std::process::exit(2);
    }
}
