use std::io::{self, Read, Write};

fn invalid() -> ! {
    let _ = io::stderr().lock().write_all(b"error: invalid input\n");
    std::process::exit(2);
}

fn main() {
    if std::env::args_os().skip(1).next().is_some() {
        invalid();
    }

    let stdin = io::stdin();
    let mut reader = stdin.lock().take(65_537);
    let mut bytes = Vec::with_capacity(65_537);
    if reader.read_to_end(&mut bytes).is_err() {
        invalid();
    }
    if bytes.len() > 65_536 || bytes.starts_with(&[0xEF, 0xBB, 0xBF]) {
        invalid();
    }
    if bytes.contains(&b'\r') {
        invalid();
    }
    let text = match std::str::from_utf8(&bytes) {
        Ok(text) => text,
        Err(_) => invalid(),
    };

    // Validate every retained line before classifying any line.
    let mut lines = Vec::with_capacity(100);
    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        if line.len() > 256 || lines.len() == 100 {
            invalid();
        }
        lines.push(line);
    }

    let mut output = String::from("{\"positions\":[");
    let mut first = true;
    for (index, line) in lines.iter().enumerate() {
        if matches!(line.as_bytes().last(), Some(&b' ') | Some(&b'\t')) {
            if !first {
                output.push(',');
            }
            first = false;
            output.push_str(&(index + 1).to_string());
        }
    }
    output.push_str("]}\n");

    let stdout = io::stdout();
    let mut writer = stdout.lock();
    if writer.write_all(output.as_bytes()).is_err() || writer.flush().is_err() {
        std::process::exit(1);
    }
}
