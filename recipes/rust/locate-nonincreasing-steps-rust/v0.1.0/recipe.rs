use std::io::{self, Read, Write};

fn invalid_input() -> ! {
    let _ = io::stderr().lock().write_all(b"error: invalid input\n");
    std::process::exit(2);
}

fn prepare_output() -> Result<String, ()> {
    let mut bytes = Vec::new();
    io::stdin()
        .lock()
        .take(65537)
        .read_to_end(&mut bytes)
        .map_err(|_| ())?;
    if bytes.len() > 65536 {
        return Err(());
    }

    let text = std::str::from_utf8(&bytes).map_err(|_| ())?;
    if text.starts_with('\u{feff}') || text.as_bytes().contains(&b'\r') {
        return Err(());
    }

    // Enforce all retained-line limits before interpreting any number.
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

    let mut values = Vec::with_capacity(lines.len());
    for line in lines {
        let digits = line.as_bytes();
        if digits.len() > 1 && digits[0] == b'0' {
            return Err(());
        }
        let mut value = 0u32;
        for &digit in digits {
            if !digit.is_ascii_digit() {
                return Err(());
            }
            // The preceding iteration guarantees value <= 1,000,000,
            // so this arithmetic cannot overflow u32.
            value = value * 10 + u32::from(digit - b'0');
            if value > 1_000_000 {
                return Err(());
            }
        }
        values.push(value);
    }

    // All input is valid before constructing the successful response.
    let mut output = String::from("{\"positions\":[");
    let mut first = true;
    for i in 1..values.len() {
        if values[i] <= values[i - 1] {
            if !first {
                output.push(',');
            }
            first = false;
            output.push_str(&(i + 1).to_string());
        }
    }
    output.push_str("]}\n");
    Ok(output)
}

fn main() {
    if std::env::args_os().skip(1).next().is_some() {
        invalid_input();
    }
    let output = match prepare_output() {
        Ok(output) => output,
        Err(()) => invalid_input(),
    };
    if io::stdout().lock().write_all(output.as_bytes()).is_err() {
        // Output-write failures are outside the input-error guarantee.
        std::process::exit(2);
    }
}
