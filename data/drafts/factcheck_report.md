# Fact-check report: data/istanbul.jsonl -> data/drafts/places_checked.jsonl

Checked against English and Turkish Wikipedia on 2026-10-28. 13 of 51 entries changed (10 text fixes, 3 district-only fixes).

## Changed entries

| id | What was wrong | What changed | Source |
|---|---|---|---|
| ayasofya | Museum period given as 1934-2020; Wikipedia says the decree was 1934 but it opened as a museum in 1935. "Built in 537" is the completion year. | "1935-2020 arasında"; "532-537 yılları arasında ... inşa edildi" | https://tr.wikipedia.org/wiki/Ayasofya |
| sultanahmet-camii | Built 1609-1617, not 1616. 1616 appears only on some inscriptions. | "between 1609 and 1617" | https://en.wikipedia.org/wiki/Blue_Mosque,_Istanbul |
| misir-carsisi | District "Eminönü" is a quarter, not an ilçe | district -> Fatih | https://en.wikipedia.org/wiki/Spice_Bazaar |
| kiz-kulesi | "Reopened as a museum": Wikipedia only says the restoration (2021-2023) ended and it reopened to the public in May 2023 | "2021'de başlayan restorasyonun ardından Mayıs 2023'te yeniden ziyarete açıldı" | https://tr.wikipedia.org/wiki/K%C4%B1z_Kulesi |
| dolmabahce | "Completed in 1856": Wikipedia says built 1843-1853 (court moved there in 1856) | "built between 1843 and 1853 as the new seat" | https://en.wikipedia.org/wiki/Dolmabah%C3%A7e_Palace |
| balik-ekmek | District "Eminönü" is not an ilçe | district -> Fatih | https://tr.wikipedia.org/wiki/Bal%C4%B1k_ekmek |
| adalar | Said the archipelago consists of 4 islands; it has 9 (4 large + 5 small) | "Dokuz adadan oluşan takımadanın en büyükleri Büyükada, Heybeliada, Burgazada ve Kınalıada'dır" | https://tr.wikipedia.org/wiki/Adalar |
| emirgan | "Milyonlarca lale": no figure on Wikipedia (festival every April is confirmed) | "her Nisan düzenlenen Lale Festivali'nde rengârenk lalelerle bir çiçek bahçesine dönüşür" | https://tr.wikipedia.org/wiki/Emirg%C3%A2n_Korusu |
| camlica | "One of the highest points" and "views of the Bosphorus bridges" not supported; Wikipedia gives 288 m and views of the southern Bosphorus and the mouth of the Golden Horn | First sentence rewritten to those facts | https://en.wikipedia.org/wiki/%C3%87aml%C4%B1ca_Hill |
| bogaz-turu | District "Eminönü" is not an ilçe | district -> Fatih | https://tr.wikipedia.org/wiki/%C5%9Eehir_Hatlar%C4%B1 |
| marmaray | Called a railway tunnel; it is a commuter rail line that runs through an undersea tunnel | "Boğaz'ın altındaki tünelden geçen banliyö demiryolu hattı" | https://tr.wikipedia.org/wiki/Marmaray |
| cemberlitas-hamami | Stated as designed by Sinan; Wikipedia: "often attributed to" Sinan, commissioned by Nurbanu Sultan | "built in 1584 for Nurbanu Sultan and often attributed to Mimar Sinan" | https://en.wikipedia.org/wiki/%C3%87emberlita%C5%9F_Hamam |
| rahmi-koc | Submarine TCG Uluçalireis left the museum (2023 to Gölcük, 2024 permanently to Çanakkale) | "gezilebilen bir denizaltı" -> "tarihi tekneler" | https://tr.wikipedia.org/wiki/Rahmi_M._Ko%C3%A7_M%C3%BCzesi |

## Claims kept but not verifiable on Wikipedia (either way)

- balik-ekmek: drinking turşu suyu with it; "Galata Köprüsü'nün dibinde" (Wikipedia only says Eminönü square, from boats).
- simit: carts being red; sold "from early morning" (Wikipedia: trolleys or trays on the head).
- kadikoy-carsi: pickle shops, coffee roasters, small meyhanes (fish and food market by the pier is confirmed).
- serpme-kahvalti: the Beşiktaş kahvaltıcılar street, and the specific dishes (bal-kaymak, menemen, sucuklu yumurta, unlimited tea). There is no tr article for Turkish breakfast, so wiki_tr is null.
- midye-dolma: especially popular late at night.
- baklava: served with kaymak. The claim that Karaköy is a popular place for baklava is supported by tr "Karaköy".
- meyhane: fasıl music; Kadıköy meyhanes (Asmalımescit and Nevizade are supported).
- pierre-loti: "Eyüp Sultan Camii'nin arkasındaki tepe" (the hill, gondola and walk through the cemetery are confirmed).
- moda: sitting on the rocks at sunset; view of the historic peninsula skyline (tea gardens and ice cream are confirmed).
- bogaz-turu: "the cheapest way to see the city from the sea".
- marmaray: Sirkeci-Üsküdar in "a few minutes".
- nostaljik-tramvay: the trams being red.
- istanbul-modern: the café having a sea view (Wikipedia confirms a café and restaurant).
- sahaflar: shaded courtyard; calligraphy and engravings.
- bebek-arnavutkoy: long waterside walking path.
- istanbulkart: topping up "with cash or card" (machines, kiosks and offices are confirmed).

## Notes

- pierre-loti: the tr article "Pierre Loti Tepesi" has no coordinates and there is no en article for the hill. lat/lon come from en "Piyer Loti Museum", the café on the hilltop. wiki_en is null.
- belgrad-ormani: Wikipedia says the forest is split between Sarıyer and Eyüpsultan. District kept as Sarıyer.
- emirgan, tunel, rahmi-koc: their Wikipedia articles have no coordinates, so lat/lon are null.
- bebek-arnavutkoy: verified against "Arnavutköy" (wooden mansions, European shore). "Bebek, Beşiktaş" also exists.
- yagmurlu-gun: source is "Historic Areas of Istanbul"; lat/lon are null by design.
