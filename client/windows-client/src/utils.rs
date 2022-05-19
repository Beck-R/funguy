use regex::Regex;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use winreg::enums::*;
use winreg::RegKey;

pub fn calculate_hash<T: Hash>(t: &T) -> u64 {
    /*
    may need to hash differently,
    because function only returns u64,
    so someone could theoretically bruteforce the random_input
    */

    let mut s: DefaultHasher = DefaultHasher::new();
    t.hash(&mut s);
    s.finish()
}

pub fn get_uuid() -> String {
    let regex: Regex = Regex::new(r"\{|\}|").unwrap();

    let hklm: RegKey = RegKey::predef(HKEY_LOCAL_MACHINE);
    let key: RegKey = hklm.open_subkey("SYSTEM\\HardwareConfig\\").unwrap();
    let raw_uuid: String = key.get_value("LastConfig").unwrap();

    let uuid: String = regex.replace_all(&raw_uuid, "").to_string();

    return uuid;
}
