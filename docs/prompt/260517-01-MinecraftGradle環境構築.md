# 260517-01 Minecraft Forge mod Gradle ビルド環境構築

**相談日**: 2026年5月17日

## ユーザー依頼

> `gradle build` を実行したら `CommandNotFoundException` が出てビルドできない。

## 回答内容

### 問題の特定

- `gradle` コマンドが PATH に存在しない
- インストール済み Java が `C:\Windows\system32\java.exe`（Java 6 / JRE）のみで、Forge 必須の **Java 17** がなかった

### 対応手順

1. **Java 17 JDK インストール**
   ```powershell
   winget install EclipseAdoptium.Temurin.17.JDK
   # → C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot にインストール
   ```

2. **Gradle 8.4 手動インストール**（winget に Gradle.Gradle パッケージなし）
   ```powershell
   Invoke-WebRequest -Uri "https://services.gradle.org/distributions/gradle-8.4-bin.zip" -OutFile "$env:TEMP\gradle-8.4-bin.zip"
   Expand-Archive -Path "$env:TEMP\gradle-8.4-bin.zip" -DestinationPath "C:\" -Force
   # → C:\gradle-8.4\bin\gradle.bat に展開
   ```

3. **Gradle Wrapper 生成**
   ```powershell
   $env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot"
   $env:PATH = "C:\gradle-8.4\bin;" + $env:PATH + ";" + $env:JAVA_HOME + "\bin"
   Set-Location "C:\ai\minecraft-pokemon"
   gradle wrapper --gradle-version 8.4
   # → gradlew.bat / gradlew / gradle/wrapper/ を生成
   ```

4. **ビルド実行**
   ```powershell
   $env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot"
   .\gradlew build
   # → BUILD SUCCESSFUL
   ```

## 反映済みアクション

- `C:\ai\minecraft-pokemon\gradlew.bat` 生成
- `C:\ai\minecraft-pokemon\gradlew` 生成
- `C:\ai\minecraft-pokemon\gradle\wrapper\gradle-wrapper.jar` 生成
- `C:\ai\minecraft-pokemon\gradle\wrapper\gradle-wrapper.properties` 生成
- ビルド成功（`build/libs/` に MOD JAR 出力）

## 注意事項

- ターミナルを再起動するたびに `$env:JAVA_HOME` の再設定が必要
- 恒久化するには Windows の「システム環境変数」で `JAVA_HOME` を設定する
- `.\gradlew build`（Wrapper 経由）を使えば以後 Gradle 本体のインストール不要

## プロジェクト情報

- プロジェクト: `C:\ai\minecraft-pokemon`
- Forge バージョン: `1.20.1-47.2.20`
- ForgeGradle: `6.0.53`
- Java: 17（Temurin）
- Gradle: 8.4

## 関連ファイル

- [build.gradle](../../../ai/minecraft-pokemon/build.gradle)
- [settings.gradle](../../../ai/minecraft-pokemon/settings.gradle)
