use std::io::{self, Read, Write};

fn invalid_input() -> ! {
    let _ = io::stderr().lock().write_all(b"error: invalid input\n");
    std::process::exit(2);
}

fn prepare_output() -> Result<String, ()> {
    if std::env::args_os().skip(1).next().is_some() {
        return Err(());
    }

    let mut input = Vec::new();
    io::stdin()
        .lock()
        .take(65_537)
        .read_to_end(&mut input)
        .map_err(|_| ())?;

    if input.len() > 65_536 {
        return Err(());
    }
    let text = std::str::from_utf8(&input).map_err(|_| ())?;
    if text.starts_with('\u{feff}') || input.contains(&b'\r') {
        return Err(());
    }

    // Validate every retained line before classifying any spelling.
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

    let mut output = String::from("{\"valid\":[");
    for (index, line) in lines.iter().enumerate() {
        let bytes = line.as_bytes();
        let first_ok = bytes[0].is_ascii_alphabetic() || bytes[0] == b'_';
        let rest_ok = bytes[1..]
            .iter()
            .all(|b| b.is_ascii_alphanumeric() || *b == b'_');
        if index != 0 {
            output.push(',');
        }
        output.push_str(if first_ok && rest_ok { "true" } else { "false" });
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
