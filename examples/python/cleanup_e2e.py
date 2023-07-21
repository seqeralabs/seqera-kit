from tw_pywrap import tower

# Create an instance of the Tower class
tw = tower.Tower()

# Run the org delete command with arguments
tw.organizations("delete", 
                 "--name", 
                 "tw-pywrap-e2e")