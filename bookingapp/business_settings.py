# This file contains non-technical (business) settings for the booking app,
# all neatly stacked in one place.

# Lesson price map. Format: price:num_hours
price_map = {
    550: 1,
    2600: 5,
    5000: 10
}


# Length of one booking slot (in minutes)
booking_slot_length = 30

# Length of one lesson
# Caution: This will be moved to a Course property in the future
# so that different courses can have different class length
lesson_length = 60          

# The student may only book no earlier than this # of hrs in advance
policy_book_hours = 48 

# The student may only cancel no earlier than this # of hrs in advance
policy_unbook_hours = 24

# The schedule will be populated this # of days in advance
policy_populate_schedule_days = 7