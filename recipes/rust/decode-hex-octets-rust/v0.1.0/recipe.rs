use std::io::{self, Read, Write};
use std::str;

fn nibble(byte: u8) -> Result<u8, ()> {
    match byte {
        b'0'..=b'9' => Ok(byte - b'0'),
        b'a'..=b'f' => Ok(byte - b'a' + 10),
        _ => Err(()),
    }
}

fn decode() -> Result<String, ()> {
    if std::env::args_os().skip(1).next().is_some() {
        return Err(());
    }

    let stdin = io::stdin();
    let mut input = Vec::with_capacity(65_537);
    stdin.lock().take(65_537).read_to_end(&mut input).map_err(|_| ())?;
    if input.len() > 65_536 {
        return Err(());
    }

    let text = str::from_utf8(&input).map_err(|_| ())?;
    if text.starts_with('\u{feff}') || text.as_bytes().contains(&b'\r') {
        return Err(());
    }

    // Enforce all retained-line limits before classifying any token.
    let mut lines = Vec::with_capacity(100);
    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        if line.len() > 256 || lines.len() == 100 {
            return Err(());
        }
        lines.push(line);
    }

    let mut values = Vec::with_capacity(lines.len());
    for line in lines {
        let token = line.as_bytes();
        if token.len() != 2 {
            return Err(());
        }
        let high = nibble(token[0])?;
        let low = nibble(token[1])?;
        values.push(high * 16 + low);
    }

    let mut output = String::with_capacity(412);
    output.push_str("{\"bytes\":[");
    for (index, value) in values.iter().enumerate() {
        if index != 0 {
            output.push(',');
        }
        output.push_str(&value.to_string());
    }
    output.push_str("]}\n");
    Ok(output)
}

fn main() {
    match decode() {
        Ok(output) => {
            let stdout = io::stdout();
            if stdout.lock().write_all(output.as_bytes()).is_err() {
                std::process::exit(2);
            }
        }
        Err(()) => {
            let stderr = io::stderr();
            let _ = stderr.lock().write_all(b"error: invalid input\n");
            std::process::exit(2);
        }
    }
}
