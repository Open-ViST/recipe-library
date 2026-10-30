use std::fmt::Write as FmtWrite;
use std::io::{self, Read, Write};

struct Network<'a> {
    input: &'a str,
    network: u64,
    last: u64,
    prefix: u32,
    count: u64,
    host_bits_set: bool,
}

fn decimal(text: &str, maximum: u32) -> Result<u32, ()> {
    let bytes = text.as_bytes();
    if bytes.is_empty() || (bytes.len() > 1 && bytes[0] == b'0') {
        return Err(());
    }
    let mut value = 0u32;
    for &byte in bytes {
        if !byte.is_ascii_digit() {
            return Err(());
        }
        value = value.checked_mul(10).ok_or(())?
            .checked_add(u32::from(byte - b'0')).ok_or(())?;
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
        let octet = decimal(parts.next().ok_or(())?, 255)?;
        address = address * 256 + u64::from(octet);
    }
    if parts.next().is_some() {
        return Err(());
    }
    Ok(address)
}

fn dotted(address: u64) -> String {
    format!("{}.{}.{}.{}",
        (address >> 24) & 255,
        (address >> 16) & 255,
        (address >> 8) & 255,
        address & 255)
}

fn prepare() -> Result<String, ()> {
    let mut bytes = Vec::new();
    {
        let stdin = io::stdin();
        let mut limited = stdin.lock().take(65537);
        limited.read_to_end(&mut bytes).map_err(|_| ())?;
    }
    if bytes.len() > 65536 {
        return Err(());
    }
    let text = std::str::from_utf8(&bytes).map_err(|_| ())?;
    // This also rejects a leading UTF-8 BOM.
    if !text.is_ascii() {
        return Err(());
    }

    let mut records = Vec::new();
    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        if records.len() >= 100 {
            return Err(());
        }
        let (address_text, prefix_text) = line.split_once('/').ok_or(())?;
        let address = ipv4(address_text)?;
        let prefix = decimal(prefix_text, 32)?;
        // The left operand is u64, so even the /0 shift by 32 is valid.
        let count = 1u64 << (32 - prefix);
        let network = (address / count) * count;
        let last = network + count - 1;
        records.push(Network {
            input: line,
            network,
            last,
            prefix,
            count,
            host_bits_set: address != network,
        });
    }

    // All input is validated before constructing the success response.
    let mut output = String::from("{\"networks\":[");
    for (index, record) in records.iter().enumerate() {
        if index != 0 {
            output.push(',');
        }
        // Validated input contains only digits, dots and one slash,
        // so embedding it in a JSON string requires no escaping.
        write!(
            &mut output,
            "{{\"input\":\"{}\",\"network\":\"{}\",\"last\":\"{}\",\"prefix\":{},\"address_count\":{},\"host_bits_set\":{}}}",
            record.input,
            dotted(record.network),
            dotted(record.last),
            record.prefix,
            record.count,
            record.host_bits_set
        ).map_err(|_| ())?;
    }
    output.push_str("]}\n");
    Ok(output)
}

fn invalid() -> ! {
    let stderr = io::stderr();
    let _ = stderr.lock().write_all(b"error: invalid input\n");
    std::process::exit(2)
}

fn main() {
    if std::env::args_os().skip(1).next().is_some() {
        invalid();
    }
    let output = match prepare() {
        Ok(output) => output,
        Err(()) => invalid(),
    };
    let stdout = io::stdout();
    if stdout.lock().write_all(output.as_bytes()).is_err() {
        std::process::exit(2);
    }
}
