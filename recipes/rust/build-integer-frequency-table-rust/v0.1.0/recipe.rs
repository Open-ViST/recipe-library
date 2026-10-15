use std::io::{self, Read, Write};
use std::collections::BTreeMap;

fn invalid_input() -> ! {
    let _ = io::stderr().lock().write_all(b"error: invalid input\n");
    std::process::exit(2);
}

fn prepare_output() -> Result<String, ()> {
    let stdin = io::stdin();
    let mut reader = stdin.lock().take(65_537);
    let mut input = Vec::new();
    reader.read_to_end(&mut input).map_err(|_| ())?;
    if input.len() > 65_536 {
        return Err(());
    }

    let text = std::str::from_utf8(&input).map_err(|_| ())?;
    if text.starts_with('\u{feff}') || text.contains('\r') {
        return Err(());
    }

    // Enforce all retained-line limits before parsing or grouping values.
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

    let mut values = Vec::new();
    for line in lines {
        let bytes = line.as_bytes();
        if bytes.len() > 1 && bytes[0] == b'0' {
            return Err(());
        }
        let mut value = 0u32;
        for &byte in bytes {
            if !byte.is_ascii_digit() {
                return Err(());
            }
            // The previous value is at most 1,000,000, so this cannot overflow.
            value = value * 10 + u32::from(byte - b'0');
            if value > 1_000_000 {
                return Err(());
            }
        }
        values.push(value);
    }

    let mut frequencies = BTreeMap::<u32, u32>::new();
    for value in values {
        *frequencies.entry(value).or_insert(0) += 1;
    }

    let mut output = String::from("{\"frequencies\":[");
    let mut first = true;
    for (value, count) in frequencies {
        if !first {
            output.push(',');
        }
        first = false;
        output.push_str(&format!("[{},{}]", value, count));
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

    let stdout = io::stdout();
    let mut writer = stdout.lock();
    if writer.write_all(output.as_bytes()).is_err() || writer.flush().is_err() {
        std::process::exit(2);
    }
}
