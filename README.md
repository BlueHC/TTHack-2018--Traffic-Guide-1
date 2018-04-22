# Readme

The content in this repository was created during the <blue hackers club/>-Hackathon in April 2018

## Gruppenname

Last Men Standing

## Name der Challenge

"To drive or not to drive" - Traffic Guide

## Challengebeschreibung

Ziel der Challenge:
Entwicklung eines Simulators zur Darstellung des Verkehrsflusses im Hamburger Nahverkehr und der Änderung des Verkehrsflusses bei Sperrung einer bestimmten Strecke.

Hintergrund: Katrin managt den ÖPNV in Hamburg. Für den folgenden Tag ist ein großes Orkantief angekündigt und es wird voraussichtlich viele Streckensperrungen geben. Katrin würde gern verstehen wie sich Reisende während so einer Ausnahmesituation verhalten, um den kommenden Tag vorzuplanen.

## Kurzbeschreibung der entwickelten Lösung:

Wir haben eine Simulation entwickelt, die vorhersagt, wie sich die Fahrgäste im Falle einer Sperrung auf Verkehrsmittel verteilen. Hierzu haben wir betrachtet, ob die Passagiere um ihr Ziel zu erreichen auf eine andere Route des HVV, ein Mobility Sharing-Angebot oder ein StadtRAD umsteigen können oder gar zu Fuß ankommen. Unsere Lösung berücksichtigt echte Live-Daten zur Verfügbarkeit von Rädern an StadtRAD-Stationen, von mobility Sharing-Anbietern wie eMio und cambio, sowie Wetter-Daten. Die simulierten Daten werden dem HVV als Entscheidungsgrundlage in einem Front-End als Wasserfall-Diagramm aufbereitet.

Als besonderes Feature haben wir ein neuronales Netz gebaut, dass darauf trainiert werden kann das Verhalten der Fahrgäste zu simulieren. Sollte nun der HVV seine echten Daten über das Passagierverhalten in unser Modell einspeisen, wird dieses kontinuierlich besser darin das Verhalten vorherzusagen.

## Namen und Kontaktdaten der Gruppenmitglieder:
Hauke Diers, hauke.diers@outlook.com
Marlon Flügge, marlon.fluegge@web.de
Merlin Burri, merlin.burri@gmail.com
Tilman Ihrig, tilmangm@gmail.com
Andreas Thinius, cycleguide@web.de
