## cryptopaper-2  &nbsp;&nbsp;  :chart_with_upwards_trend: ![#StandWithUkraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraineFlat.svg) :newspaper:
<img src="https://github.com/KF-R/cryptopaper-2/assets/6677966/a40c3ae7-8288-450b-a5f6-7d01a316a1cc.png" width="50%" height="50%" align="right" />

**An updated BTC/LTC/USD dashboard with scraped headlines, topical statistics and data from on-going global crises.**

Designed with high-visibility and at-a-glance updates in mind.  Intended for 2200x1650* e-paper devices such as the Boox Mira.  Well suited to low power instrumentation.

**&lt;UP&gt;** and **&lt;DOWN&gt;** keys will adjust contrast

### From left to right from top to bottom:
- Time, Date, BTC/USD Spot
- Headlines from BBC world news*
- BTC/USD high and low during the last six hours
- Main BTC/USD chart for the last six hours
- Extra charts and data from world events (Currently: monthly invaders "_knocked out cold_" and BTCRUB)
- Volatility Indicator

    The marker in the vertical box indicates level of current spot price relative to high/low.
    
    If the inner circle fills the outer circle, there's been around 10% movement (or more) during the last six hours.
    
    Spread and change for this period are also shown above and below on its right hand side.
 
    This is also where you'll find the digital clock's analogue second hand.
  
- Weather for specified location
- Location, IP address, contrast setting, uptime
- Time since last update for each dataset (_if > 1 minute; else hidden_)
- Current LTC value in USD (_calculated from latest LTCBTC and BTC spot values_)
- Version number
- Current LTCBTC rate

<br/>

\* _Headlines will flash (alternating inverted state) if they match any of a set of words defined in lib/watch-words.txt._

---

### Installation:

    git clone https://github.com/KF-R/cryptopaper-2
    cd cryptopaper-2
    pip install -r requirements.txt

Optionally, if you would like to run it directly on linux or macs:

    mv cryptopaper.py cryptopaper
    chmod +x cryptopaper

Now you can run it from the command line with ```./cryptopaper```.

### Usage:

Browse to the local URL, by default: https://127.0.0.1:5000/

---

### Customizations:

- Watch Words

    `lib/watch-words.txt` contains an editable list of newline-separated search strings.<br/>Any headline containing any of these strings will flash (toggling inverted status every other second).
    
- Options

    The weather locale is set by editing the `LOCATION` constant in `cryptopaper-2.py`. <br/>This string is fed to the most excellent [wttr.in](https://github.com/chubin/wttr.in), so any location strings valid there should also work here.<br/>You can also adjust the server `PORT` here, if necessary.

- Sources

    Headlines are fetched from BBC World News (https://www.bbc.com/news/world).<br/>BTC and LTC data pulled from Bitstamp (https://www.bitstamp.net).<br/>Extra data pulled from https://russian-casualties.in.ua/ and Coindesk (https://www.coindesk.com).
    
