# KeyAtome
![GitHub release](https://img.shields.io/github/release/jugla/KeyAtome)

Home Assistant component to handle key atom, a Linky-compatible device made by Total/Direct-Energie.

## Installation
Either use HACS (default), either manual
### [HACS](https://hacs.xyz/) (Home Assistant Community Store) [under request]
1. Go to HACS page on your Home Assistant instance 
1. Select `integration` 
1. Press add icon and search for `worldtidesinfocustom` 
1. Select worldtidesinfocustom and install 

### Manual
<details><summary>Manual Procedure</summary>
  
1. Download the folder worldtidesinfocustom from the latest [release](https://github.com/jugla/worldtidesinfocustom/releases) (with right click, save 
link as) 
1. Place the downloaded directory on your Home Assistant machine in the `config/custom_components` folder (when there is no `custom_components` folder in the 
folder where your `configuration.yaml` file is, create it and place the directory there) 
1. restart HomeAssistant
</details>

## Using the component
in configuration.yaml, declare :

*Example of YAML*
  
```yaml
##configuration.yaml example
sensor:
  - platform: keyatome
    username: YOUR_ATOME_USERNAME
    password: YOUR_ATOME_PASSWORD
```

**Check that *atome* of HomeAssistant is not activated (i.e. declared in configuration.yaml) to avoid too many request on Atome Server and conflict name for sensors name**

## Breaking changes
The first version reprensents the Atom component in Home Assistant 2021.12.4 (@baqs)
This library is a fork of this in order to implement new feature.

For release V0.0.1 and V1.0.0 : the name of sensor are `sensor.key_atome_xxx`

Since release V2.0.0 : the name of sensor are `sensor.atome_xxx` (like HA atome component)


## Acknowledgments
* Thanks to the 1rst implementation performed by BaQs for Home Assistant.
* This project is a fork of atome components in HA


