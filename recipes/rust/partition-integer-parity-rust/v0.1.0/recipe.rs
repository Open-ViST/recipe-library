use std::io::{self, Read, Write};

fn invalid_input() -> ! {
    let _ = io::stderr().lock().write_all(b"error: invalid input\n");
    std::process::exit(2);
}

fn prepare_output() -> Result<String, ()> {
    let stdin = io::stdin();
    let mut reader = stdin.lock().take(65_537);
    let mut bytes = Vec::new();
    reader.read_to_end(&mut bytes).map_err(|_| ())?;
    if bytes.len() > 65_536 {
        return Err(());
    }

    let text = std::str::from_utf8(&bytes).map_err(|_| ())?;
    if bytes.starts_with(&[0xEF, 0xBB, 0xBF]) || text.contains('\r') {
        return Err(());
    }

    // Establish every line-count and line-length limit before parsing values.
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
        let digits = line.as_bytes();
        if digits.len() > 1 && digits[0] == b'0' {
            return Err(());
        }
        let mut value = 0u32;
        for &digit in digits {
            if !digit.is_ascii_digit() {
                return Err(());
            }
            value = value.checked_mul(10)
                .and_then(|v| v.checked_add(u32::from(digit - b'0')))
                .ok_or(())?;
            if value > 1_000_000 {
                return Err(());
            }
        }
        values.push(value);
    }

    // All input is now validated. Scan in input order for each partition.
    let mut output = String::from("{\"even\":[");
    for parity in 0..2u32 {
        if parity == 1 {
            output.push_str("],\"odd\":[");
        }
        let mut first = true;
        for &value in &values {
            if value % 2 == parity {
                if !first {
                    output.push(',');
                }
                first = false;
                output.push_str(&value.to_string());
            }
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
    let stdout = io::stdout();
    let mut writer = stdout.lock();
    if writer.write_all(output.as_bytes()).is_err() || writer.flush().is_err() {
        std::process::exit(1);
    }
}
