# Examples  
* <a href='https://github.com/r-kan/iReminder/blob/master/example/case1.run'>case1.run</a>: Grasp cared picture  
_I admire the work of Immanuel Kant, especially on the talk of ethics. I would like to see how those words are valued nowadays._  
```
./iReminder "Kant famous" -c config.ini
```
* <a href='https://github.com/r-kan/iReminder/blob/master/example/case2.run'>case2.run</a>: Give reminder  
_A reminder of the diet plan before dinner time might be quite beneficial._  
```
./iReminder diet.json
```
Check the content of <a href='https://github.com/r-kan/iReminder/blob/master/example/diet.json'>diet.json</a>.  
You need to modify the value of `location` with a directory of pictures, and probably, the `period` value, or you may see nothing.  

```json
// file 'diet.json'
{
  "image":
  {
    "diet": {"location": "/Users/rkan/diet_picture", "rank": {"period": "1600-1700"}}
  }
}
```
Note that this example also demonstrates the feature without using Google Custom Search.  

* <a href='https://github.com/r-kan/iReminder/blob/master/example/case3.run'>case3.run</a>: Train subconscious  
_The subconscious mind, which thinks in images and feelings, has such a great power. Visualize our goal, with images and motivated phrases, can thus be a way harness this power to our advantage._  
```
./iReminder dream patience -p maxim.list -c config.ini
```
Check the content of <a href='https://github.com/r-kan/iReminder/blob/master/example/maxim.list'>maxim.list</a>, and try add more maxims to see how it works.

```
// file 'maxim.list'
Living without an aim is like sailing without a compass
Patience is bitter, but its fruit is sweet
```
