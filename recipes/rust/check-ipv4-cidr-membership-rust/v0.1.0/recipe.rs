use std::io::{self, Read, Write};

fn decimal(text: &str, maximum: u64) -> Result<u64, ()> {
    let bytes = text.as_bytes();
    if bytes.is_empty() || (bytes.len() > 1 && bytes[0] == b'0') {
        return Err(());
    }
    let mut value = 0u64;
    for &byte in bytes {
        if !byte.is_ascii_digit() {
            return Err(());
        }
        value = value * 10 + u64::from(byte - b'0');
        if value > maximum {
            return Err(());
        }
    }
    Ok(value)
}

fn ipv4(text: &str) -> Result<u64, ()> {
    let mut parts = text.split('.');
    let mut address = 0u64;
    for _ in 0..4 {
        let part = parts.next().ok_or(())?;
        address = address * 256 + decimal(part, 255)?;
    }
    if parts.next().is_some() {
        return Err(());
    }
    Ok(address)
}

fn prepare() -> Result<String, ()> {
    let stdin = io::stdin();
    let mut reader = stdin.lock().take(65537);
    let mut bytes = Vec::new();
    reader.read_to_end(&mut bytes).map_err(|_| ())?;
    if bytes.len() > 65536 {
        return Err(());
    }
    let text = std::str::from_utf8(&bytes).map_err(|_| ())?;
    if text.starts_with('\u{feff}') || !text.is_ascii() {
        return Err(());
    }

    let mut checks = Vec::new();
    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        if checks.len() == 100 {
            return Err(());
        }
        let (address_text, cidr_text) = line.split_once(' ').ok_or(())?;
        let address = ipv4(address_text)?;
        let (network_text, prefix_text) = cidr_text.split_once('/').ok_or(())?;
        let network_address = ipv4(network_text)?;
        let prefix = decimal(prefix_text, 32)?;
        let size = 1u64 << (32u64 - prefix);
        let network = (network_address / size) * size;
        if network_address != network {
            return Err(());
        }
        let last = network + size - 1;
        let contains = address >= network && address <= last;
        checks.push((address_text, cidr_text, contains));
    }

    // All input has been validated before constructing successful output.
    // Accepted address and CIDR spellings need no JSON escaping.
    let mut output = String::from("{\"checks\":[");
    for (index, &(address, cidr, contains)) in checks.iter().enumerate() {
        if index != 0 {
            output.push(',');
        }
        output.push_str("{\"address\":\"");
        output.push_str(address);
        output.push_str("\",\"cidr\":\"");
        output.push_str(cidr);
        output.push_str("\",\"contains\":");
        output.push_str(if contains { "true" } else { "false" });
        output.push('}');
    }
    output.push_str("]}\n");
    Ok(output)
}

fn invalid_input() -> ! {
    let stderr = io::stderr();
    let mut error = stderr.lock();
    let _ = error.write_all(b"error: invalid input\n");
    let _ = error.flush();
    std::process::exit(2);
}

fn main() {
    if std::env::args_os().skip(1).next().is_some() {
        invalid_input();
    }
    let output = match prepare() {
        Ok(output) => output,
        Err(()) => invalid_input(),
    };
    let stdout = io::stdout();
    let mut writer = stdout.lock();
    if writer.write_all(output.as_bytes()).is_err() || writer.flush().is_err() {
        std::process::exit(2);
    }
}
