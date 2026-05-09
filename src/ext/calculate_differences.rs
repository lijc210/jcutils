use chrono::NaiveDate;
use pyo3::prelude::*;

#[allow(unsafe_op_in_unsafe_fn)]
#[pyfunction]
pub fn calculate_differences(nums: Vec<i32>) -> (i32, i32, f64, f64) {
    let mut differences: Vec<i32> = Vec::new();

    for i in 0..nums.len() - 1 {
        let date1 = NaiveDate::parse_from_str(&nums[i].to_string(), "%Y%m%d").unwrap();
        let date2 = NaiveDate::parse_from_str(&nums[i + 1].to_string(), "%Y%m%d").unwrap();
        differences.push((date2 - date1).num_days() as i32);
    }

    let max_diff = *differences.iter().max().unwrap();
    let min_diff = *differences.iter().min().unwrap();
    let sum: i32 = differences.iter().sum();
    let average_diff = sum as f64 / differences.len() as f64;

    differences.sort();
    let median_diff = if differences.len() % 2 == 0 {
        (differences[differences.len() / 2 - 1] + differences[differences.len() / 2]) as f64 / 2.0
    } else {
        differences[differences.len() / 2] as f64
    };

    (max_diff, min_diff, median_diff, average_diff)
}
