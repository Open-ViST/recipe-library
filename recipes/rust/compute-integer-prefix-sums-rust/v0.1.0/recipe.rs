use std::io::{self, Read, Write};
use std::str;

fn invalid_input() -> ! {
    let _ = io::stderr().lock().write_all(b"error: invalid input\n");
    std::process::exit(2);
}

fn prepare_output() -> Result<String, ()> {
    if std::env::args_os().nth(1).is_some() {
        return Err(());
    }

    let mut input = Vec::new();
    io::stdin()
        .lock()
        .take(65537)
        .read_to_end(&mut input)
        .map_err(|_| ())?;
    if input.len() > 65536 {
        return Err(());
    }

    let text = str::from_utf8(&input).map_err(|_| ())?;
    if text.starts_with('\u{feff}') || text.contains('\r') {
        return Err(());
    }

    // Enforce all retained-line limits before numeric classification.
    let mut lines = Vec::new();
    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        if line.len() > 256 || lines.len() >= 100 {
            return Err(());
        }
        lines.push(line);
    }

    let mut sums: Vec<u64> = Vec::with_capacity(lines.len());
    let mut total: u64 = 0;
    for line in lines {
        let bytes = line.as_bytes();
        if bytes.len() > 1 && bytes[0] == b'0' {
            return Err(());
        }

        let mut value: u64 = 0;
        for &byte in bytes {
            if !(b'0'..=b'9').contains(&byte) {
                return Err(());
            }
            value = value * 10 + u64::from(byte - b'0');
            if value > 1_000_000 {
                return Err(());
            }
        }
        total += value;
        sums.push(total);
    }

    // Construct output only after every input value has been validated.
    let mut output = String::from("{\"sums\":[");
    for (index, sum) in sums.iter().enumerate() {
        if index != 0 {
            output.push(',');
        }
        output.push_str(&sum.to_string());
    }
    output.push_str("]}\n");
    Ok(output)
}

fn main() {
    let output = match prepare_output() {
        Ok(output) => output,
        Err(()) => invalid_input(),
    };

    let mut stdout = io::stdout().lock();
    if stdout.write_all(output.as_bytes()).is_err() || stdout.flush().is_err() {
        std::process::exit(2);
    }
}
