# it-thematic

**500 ошибка** приходит в следующем виде: 
[img](https://image.prntscr.com/image/PPcnRWzfRReB4S5pQOTkNA.png)

 Поэтому преобразование дает ошибку:

`json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`

 Тогда в бой вступает исключение на `159` строке, которое срезает строчку со словом "_ОШИБКА_"
 
