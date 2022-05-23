extern crate rdev;
extern crate windows;

use rdev::{EventType, Key::*};
use std::fs::{File, OpenOptions};
use std::io::prelude::*;

const MODIFIER_KEYS: [rdev::Key; 4] = [Alt, AltGr, MetaLeft, MetaRight];

// too lazy to do this rn
pub fn start(data_folder: String) {
    rdev::listen(move |event| {
        if let EventType::KeyPress(key) = event.event_type {
            if MODIFIER_KEYS.contains(&key) {
                return;
            } else {
            }
        }
    });
}
