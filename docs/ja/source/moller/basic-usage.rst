インストールと基本的な使い方
================================================================

**必要なライブラリ・環境**

  HTP-tools に含まれる網羅計算ツール moller を利用するには、以下のプログラムとライブラリが必要です。

  - Python 3.x
  - ruamel.yaml モジュール
  - tabulate モジュール
  - GNU Parallel (ジョブスクリプトを実行するサーバ・計算ノード上にインストールされていること)

**ソースコード配布サイト**

  - `GitHubリポジトリ <https://github.com/issp-center-dev/Moller>`_

**ダウンロード方法**

  gitを利用できる場合は、以下のコマンドでmollerをダウンロードできます。

  .. code-block:: bash

    $ git clone https://github.com/issp-center-dev/Moller.git

**インストール方法**

  mollerをダウンロード後、以下のコマンドを実行してインストールします。mollerが利用するライブラリも必要に応じてインストールされます。

  .. code-block:: bash

     $ cd ./Moller
     $ python3 -m pip install .

  実行プログラム ``moller`` および ``moller_status`` がインストールされます。

**ディレクトリ構成**

  ::

     .
     |-- LICENSE
     |-- README.md
     |-- pyproject.toml
     |-- docs/
     |   |-- ja/
     |   |-- en/
     |   |-- tutorial/
     |-- src/
     |   |-- moller/
     |       |-- __init__.py
     |       |-- main.py
     |       |-- platform/
     |       |   |-- __init__.py
     |	     |   |-- base.py
     |	     |   |-- base_slurm.py
     |	     |   |-- base_pbs.py
     |	     |   |-- base_default.py
     |	     |   |-- ohtaka.py
     |	     |   |-- kugui.py
     |	     |   |-- pbs.py
     |	     |   |-- default.py
     |	     |   |-- function.py
     |	     |   |-- utils.py
     |	     |-- moller_status.py
     |-- sample/

**基本的な使用方法**

mollerはスーパーコンピュータ向けにバッチジョブスクリプトを生成するツールです。多重実行の機能を利用して、パラメータ並列など一連の計算条件について並列にプログラムを実行します。

#. 構成定義ファイルの作成

    mollerを使用するには、まず、計算内容を記述した構成定義ファイルをYAML形式で作成します。詳細についてはファイルフォーマットの章を参照してください。

#. コマンドの実行

    作成した構成定義ファイルを入力としてmollerプログラムを実行します。バッチジョブスクリプトが生成されます。

    .. code-block:: bash

        $ moller -o job.sh input.yaml

#. バッチジョブの実行

    生成されたバッチジョブスクリプトを対象となるスーパーコンピュータシステムに転送します。
    並列実行する各パラメータごとにディレクトリを用意し、 ``list.dat`` にディレクトリ名を列挙します。
    ``list.dat`` には、ジョブを実行するディレクトリからの相対パスまたは絶対パスを記述します。

    リストファイルが用意できたらバッチジョブを投入します。
    以下では、物性研システムB(ohtaka)およびシステムC(kugui)で実行するケースをそれぞれ示します。

    - 物性研システムB(ohtaka)の場合

      ohtaka では slurm ジョブスケジューラが使用されています。バッチジョブを投入するには、バッチジョブスクリプトを引数として sbatch コマンドを実行します。ジョブスクリプト名に続けてスクリプトのパラメータを渡すことができます。パラメータとしてリストファイルを指定します。

      .. code-block:: bash

        $ sbatch job.sh list.dat

      リストファイルの指定がない場合は list.dat がデフォルトとして使われます。


    - 物性研システムC(kugui)の場合

      kugui では PBS ジョブスケジューラが使用されています。バッチジョブを投入するには、バッチジョブスクリプトを引数として qsub コマンドを実行します。スクリプトのパラメータの指定はできないので、リストファイルは list.dat として用意する必要があります。

      .. code-block:: bash

        $ qsub job.sh

#. 結果の確認

      バッチジョブ終了後に、

      .. code-block:: bash

          $ moller_status input.yaml list.dat

      を実行すると、各パラメータセットについて計算が正常に終了したかどうかを集計したレポートが出力されます。


#. ジョブの再開・再実行

    ジョブが途中で終わった場合、続けて実行するには、同じリストファイルを指定してもう一度バッチジョブを投入します。
    未実行(未完了を含む)のタスクから実行が継続されます。

    - 物性研システムB(ohtaka)の場合

      以下のように、リストファイルを指定して sbatch コマンドを実行します。

      .. code-block:: bash

        $ sbatch job.sh list.dat

      エラーで終了したタスクを再実行するには、--retry オプションを付けてバッチジョブを投入します。

      .. code-block:: bash

        $ sbatch job.sh --retry list.dat

    - 物性研システムC(kugui)の場合

      job.sh を編集して retry=0 の行を retry=1 に書き換えた後、

      .. code-block:: bash

        $ qsub job.sh

      を実行します。


**参考文献**

[1] `O. Tange, GNU Parallel - The command-Line Power Tool, ;login: The USENIX Magazine, February 2011:42-47. <https://www.usenix.org/publications/login/february-2011-volume-36-number-1/gnu-parallel-command-line-power-tool>`_
