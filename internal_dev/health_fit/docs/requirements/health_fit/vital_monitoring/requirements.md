# Use Case: Vital Monitoring Requirements

## Narrative & Scope
Patients record vital metrics through manual entry or paired devices (Omron Bluetooth blood pressure monitors, Pixel Watch / WearOS / Apple Watch wearables).

## Rules & Constraints
1. **Vital Consistency**:
   - `VitalReading.systolic_bp > VitalReading.diastolic_bp`
   - `20 <= VitalReading.heart_rate <= 250`
   - `VitalReading.weight_lbs > 10.0`
2. **Alert Triggering & Wearable Suppression**:
   - Alert is triggered when `systolic_bp >= 180`, `blood_glucose >= 300`, or manual/device `heart_rate >= 150`.
   - Wearable heart rate spikes without manual confirmation do not trigger emergency alert notifications.
3. **Rollups**:
   - `Patient.active_alert_count = count(Alert where status == 'active')`.
