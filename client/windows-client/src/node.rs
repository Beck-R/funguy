use serde::{Deserialize, Serialize};
use sysinfo::{Disk, DiskExt, ProcessorExt, System, SystemExt};

#[derive(Debug, Serialize, Deserialize)]
pub struct Drive {
    name: String,
    disk_type: String,
    fs_type: String,
    mount_point: String,
    is_removable: bool,
    total_disk: u64,

    // realtime info
    disk_usage: u64,
    disk_write: u64,
    disk_read: u64,
}

impl Drive {
    pub fn new(disk: &Disk) -> Drive {
        Drive {
            name: "not_working".to_string(), // use disk.name().to_os_string() to get actual name
            disk_type: "not_working".to_string(), // use disk.type_ to get actual type
            fs_type: String::from_utf8_lossy(disk.file_system()).to_string(),
            mount_point: disk.mount_point().display().to_string(),
            is_removable: disk.is_removable(),
            total_disk: disk.total_space() / 1000000,
            disk_usage: (disk.total_space() - disk.available_space()) / 1000000,
            disk_write: 0,
            disk_read: 0,
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Node {
    // connection info
    uuid: String,
    random_input: String,
    host_name: String,
    ipv4: String,

    // device info
    os: String,
    os_release: String,
    os_version: String,
    processor: String,
    processor_count: usize,
    min_freq: f32,
    max_freq: f32,
    memory_total: u64,
    disks: Vec<Drive>,

    // realtime info
    processor_freq: u64,
    processor_temp: u32,
    processor_usage: f32,
    memory_usage: u64,
}

impl Node {
    pub fn new(uuid: String, random_input: String, ipv4: String) -> Node {
        let mut sys: System = System::new_all();
        sys.refresh_all();

        let mut disks: Vec<Drive> = Vec::new();

        for disk in sys.disks() {
            let drive: Drive = Drive::new(disk);
            disks.push(drive);
        }

        Node {
            // connection info
            uuid,
            random_input,
            host_name: sys.host_name().unwrap(),
            ipv4,

            // device info
            os: sys.name().unwrap(),
            os_release: sys.long_os_version().unwrap(),
            os_version: sys.kernel_version().unwrap(),
            processor: sys.global_processor_info().name().to_string(),
            processor_count: sys.physical_core_count().unwrap(),
            min_freq: 0.0,
            max_freq: 0.0,
            memory_total: sys.total_memory() / 1000,
            disks: disks,

            // realtime info
            processor_freq: 0,
            processor_temp: 0,
            processor_usage: 0.0,
            memory_usage: 0,
        }
    }

    pub fn update_realtime(&mut self) {
        let mut sys: System = System::new_all();
        sys.refresh_all();

        self.processor_freq = sys.global_processor_info().frequency();
        self.processor_usage = sys.global_processor_info().cpu_usage();
        self.memory_usage = sys.used_memory() / 1000;
    }
}
