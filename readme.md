输入文件为 `input.txt`，输出文件为 `output.txt`，同时标准输出也会回显

将输入文件中表述的乐谱转换为用 `/give` 指令表示的箱装潜影盒物品

具体详情见 `resources/ref.md`

## 基础结构

```
短音

1=C

| 1' 2 3 #4 |

| 5 6, 7 b1 |
```

第 1 行的 `短音` 设定该乐谱的编曲偏好。可选值为 `短音`、`长音`。不一定需要写在第一行，文件里有一行是就行了

第 3 行的 `1=C` 为设置音高基准。

第 5、7 行，以 `|` 开头，将被识别为简谱表示的音符序列，使用空格作为分隔符，符号 `|` 在解析时将会被忽略。一条音符序列可以有任意多行，但这任意多行间需要存在空行。

支持重复空格输入，制表符将会被视作空格

以 `//` 后方的内容，包括 `//` 自身，将会视作为注释，将被忽略

更多例子：

```
长音

1=C

| 1 1 2 3 | 3 02 2 - |
```

```
短音

1=C

| 0 1 2 0 |

| 6,7, 12 3 0 |
```

## 多简谱音轨

多行简谱音符序列间存在空行时，被空行分开的两个简谱音符序列将会被视作不同的两个音轨

由空行分割出的简谱音符序列段落中，若段落包含若干行，则

例子：

```
// 多简谱音轨例子

短音

1=C

| 1 2 3 4 |         // 音轨 1
| 1' 2' 3' 4' |     // 音轨 2

| 4 3 2 1 |         // 音轨 1
| 4' 3' 2' 1' |     // 音轨 2
```

输出

```
翻译后音符序列:
简谱音轨#1: (6_C) (8_D) (10_E) (11_F) (11_F) (10_E) (8_D) (6_C)
简谱音轨#2: (18_C) (20_D) (22_E) (23_F) (23_F) (22_E) (20_D) (18_C)
```

注：简谱音轨间的长度必须一致

## 多次音符基准设置

形如 `1=C` 的这种 `1=` 开头的行，可出现若干次，每次出现后将后续的音符的基准都设置为所给值。

例子：

```
// 多次音符基准设置例子

短音

1=C
| 1 1 1 1 |

1=D
| 1 1 1 1 |
```

输出

```
翻译后音符序列:
简谱音轨#1: (6_C) (6_C) (6_C) (6_C) (8_D) (8_D) (8_D) (8_D)
```
