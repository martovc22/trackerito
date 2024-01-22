# Project Tracker
A project tracker that I made to keep track of primarily my health. My first big project, that's why it's a mess. Integrated telegram both with google sheets API to make it easier. Eventually will move to a database from google sheets


## Features
1. **Questions** (Morning, Afternoon, Evening):
   * [x] Sleep (duration, quality (1-5), heart rate during sleep, feeling rested 1-5)
   * [ ] Mood (morning, afternoon, evening)
   * [x] Meals and snacks (number, times, types)
   * [x] Hydration (water, coffee intake, alcohol)
   * [ ] Exercise (done, type, duration)
   * [x] Symptom tracking (fatigue, headaches, stomach ache, breathing difficulties, others)
   * [x] Social battery (morning and evening)
   * [x] Vitamins (Magnesium, Zinc, D, B, A, C, Others)
   * [x] Supplements (Collagen, Piracetam, Other)
   * [x] Well-being (stress, energy levels, happiness, anxiety)
   * [x] illness (cold symptoms)
   * [x] Heart palpitation (yes/no)

- All implemented via commands in a Telegram bot, provides easy and simple solution. Each input is then saved to google sheets.

## Fixes/ Things to be implemented
* [ ] Timezones (momentarily it's a mess)
* [ ] Structure
* [ ] Add a /morning, /afternoon and /evening function to make it easer
* [ ] Add notification
* [ ] Move it to Postgres
    #### To be implemented
    * [ ] Visual Analysis
    * [ ] Correlational analysis
        * [ ] heartrate and sleep
        * [ ] mood / wellbeing
        * [ ] energy levels and sleep, heartrate and heart palpitation
        * [ ] probs some more
    * [ ] Add Exercise
    * [ ] Add BMI, Weight (probably via google Fit integration)
    * [ ] Create auto calorie calculator 
    * [ ] Finances?
    * [ ] Travelling
    * [ ] Spotify tracker
        * [ ] minutes listened since 2018
        * [ ] top artis overall, long term (split into durations) and short-term
        * [ ] top 100 songs
        * [ ] top 100 songs short term
        * [ ] recommendations? 
        * [ ] most played songs
        * [ ] least played songs
    * [ ] Eventually a smart watch/ring implementation (which'd add more info about heartbeat and sleep)

## Installation

To install the project tracker, follow these steps:

1. Clone the repository: `git clone https://github.com/your-username/project-tracker.git`
2. Install dependencies: `npm install`
3. Start the application: `npm start`

I personally run ut on Docker and through fly.io

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request. 

## License

This project is licensed under the [MIT License](LICENSE).
