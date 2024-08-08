truck_ranges=("400.0" "300.0" "200.0" "100.0")
max_wait_times=("0.25" "0.5" "1.0" "2.0")
charging_times=("0.5" "1.0" "2.0" "4.0")

# Calculate the total number of jobs
total_jobs=$((${#truck_ranges[@]} * ${#max_wait_times[@]} * ${#charging_times[@]}))

i=1
for truck_range in "${truck_ranges[@]}"; do
  for max_wait_time in "${max_wait_times[@]}"; do
    for charging_time in "${charging_times[@]}"; do
        echo python source/AnalyzeTruckStopCharging.py -c ${charging_time} -m ${max_wait_time} -r ${truck_range}
        python source/AnalyzeTruckStopCharging.py -c ${charging_time} -m ${max_wait_time} -r ${truck_range} &> Logs/truck_stop_charging_c${charging_time}_m${max_wait_time}_r${truck_range}.txt &
        
        if ! ((i % 8)); then
            echo Pausing to let jobs finish
            wait
        fi
  
        echo Processed $i jobs of $total_jobs
        i=$((i+1))
    done
  done
done
