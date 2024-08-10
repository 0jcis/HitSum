# Hit$um

**Hit$um** is an easy-to-use tool that automates your war pay calculations for Torn factions. With Faction API permissions, simply enter your API key, set up the pay rates for outside chain hits, inside hits, and penalties for getting attacked. Hit$um will handle the rest, generating a unique URL for your faction members to check their earnings during or after the war.

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [War Attack Definitions](#war-attack-definitions)
- [Outside Chain Attack Calculations](#outside-chain-attack-calculations)
- [Data Fetching](#data-fetching)
- [API Call Efficiency](#api-call-efficiency)
- [Managing Links](#managing-links)
- [License](#license)
- [Contact](#contact)

## Features

- **Automated War Pay Calculations**: Automatically calculates earnings for faction members during wars.
- **Unique Tracking Links**: Generates a unique URL for each faction to monitor earnings.
- **Flexible Pay Rates**: Customize pay rates for different types of attacks and penalties.
- **Secure and Private**: Links and data are securely managed, with options to delete and refresh API keys.

## How It Works

1. **Enter API Key**: Start by entering your Faction API key.
2. **Set Up Pay Rates**: Define pay rates for outside chain hits, inside hits, and penalties for being attacked.
3. **Share the Link**: Share the unique URL with your faction members. They can use this link to check their earnings at any time during or after the war.
4. **Automatic Calculation**: Hit$um tracks all attacks and losses from the start of the war until the end, even if you register mid-war.
5. **Post-War Review**: After the war ends, members can review their final earnings and all calculations made during the war. The link remains active for 24 hours after the war concludes.

## War Attack Definitions

- **War Attack**: Any attack made by a member of your faction against a member of an opposing faction.
- **Outside Chain Attack**: An attack on a non-opponent faction member within a chain sequence leading to a bonus attack. It counts only if it occurs before the bonus attack and contributes to the chain.
- **Loss**: Recorded when an opponent successfully hits a member of your faction.

## Outside Chain Attack Calculations

The score for an outside chain attack is calculated by dividing the total score gained from all bonuses in the chain by the number of attacks made in that chain sequence.

## Data Fetching

- **Frequency**: Data is updated only when someone visits the faction's unique tracking page. Data cannot be refreshed more than once per minute.
- **Example**: If Anna checks her faction's war pay, new data is fetched. If Tom visits the page 30 seconds later, he sees Anna's data instead of triggering a new update.

## API Call Efficiency

- **Initial Data Fetch**: The first time data is fetched during a war, it may take more API calls depending on the number of chains and attacks.
- **Subsequent Fetches**: Future updates require fewer API calls since only new information is added.

## Managing Links

- **Multiple Links**: Each API key generates a new link. Multiple active tracking pages can exist, each with its own unique war pay settings.
- **Deleting API Keys**: Deleting an API key deactivates the associated link. Reusing the same API key for new tracking will remove the old link and create a new one.
- **Automatic Data Deletion**: If no one views the data for a faction for more than 7 days, all related data is automatically deleted.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions or support, feel free to contact:

- **Email**: ojcis929@gmail.com
- **GitHub**: [0jcis](https://github.com/0jcis)
