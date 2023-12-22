HPhi による *moller* 計算の例
------------------------------------------

このチュートリアルについて
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

これは、量子多体問題の正確な対角化方法を実行するためのオープンソースソフトウェアパッケージである `HPhi <https://github.com/issp-center-dev/HPhi>`__ を用いた ``moller`` の例です。
この例では、周期境界条件下の :math:`S=1/2` (``2S_1`` ディレクトリ) と :math:`S=1` (``2S_2``) 反強磁性ハイゼンベルク鎖の励起ギャップ :math:`\Delta` のシステムサイズ依存性を計算します。
``moller`` を使用することで、異なるシステムサイズの計算を並列に実行します。
これはHPhi 公式チュートリアルの `セクション 1.4 <https://issp-center-dev.github.io/HPhi/manual/develop/tutorial/en/html/zero_temperature/spin_chain.html>`__ に対応しています。

準備
~~~~~

``moller`` （HTP-tools）パッケージと ``HPhi`` がインストールされていることを確認してください。このチュートリアルでは、ISSP のスーパーコンピュータシステム ``ohtaka`` を使用して計算を実行します。

実行方法
~~~~~~~~

1. データセットを準備する

   ``2S_1``, ``2S_2`` に含まれるスクリプト ``make_inputs.sh`` を実行します。

   .. code:: bash

      $ bash ./make_inputs.sh

   ``L_8``, ``L_10``, ..., ``L_24`` (``2S_2`` の場合は ``L_18`` まで) の作業ディレクトリが生成されます。
   ディレクトリのリストは ``list.dat`` ファイルに書き込まれます。
   さらに、作業ディレクトリからエネルギーギャップを集めるためのシェルスクリプト、 ``extract_gap.sh`` が生成されます。

2. ``moller`` を使用してジョブスクリプトを生成する

   ``input.yaml`` からジョブスクリプトを生成し、 ``job.sh`` というファイル名で保存します。

   .. code:: bash

      $ moller -o job.sh input.yaml

3. バッチジョブを実行する

   ジョブリストを引数としてバッチジョブを送信します。

   .. code:: bash

      $ sbatch job.sh list.dat

4. 状態を確認する

   タスク実行の状態は ``moller_status`` プログラムによって確認できます。

   .. code:: bash

      $ moller_status input.yaml list.dat

5. 結果を集める

   計算が終了した後、ジョブからエネルギーギャップを以下のようにして集めます。

   .. code:: bash

      $ bash extract_gap.sh

   このスクリプトは、長さ :math:`L` とギャップ :math:`\Delta` のペアをテキストファイル ``gap.dat`` に書き込みます。

   結果を視覚化するために、Gnuplot ファイル ``gap.plt`` が利用可能です。
   このファイルでは、得られたギャップデータが予想される曲線によってフィットされます。

   .. math:: \Delta(L; S=1/2) = \Delta_\infty + A/L

   および

   .. math:: \Delta(L; S=1) = \Delta_\infty + B\exp(-CL).

   グラフは次のコマンドで描画できます。

   .. code:: bash

      $ gnuplot --persist gap.plt

   .. figure:: ../../../../images/tutorial_hphi_gap.*
      :alt: スピンギャップの有限サイズ効果

      スピンギャップの有限サイズ効果

   :math:`S=1/2` の場合、対数補正によりスピンギャップは有限のままです。一方で、:math:`S=1` の場合、外挿値 :math:`\Delta_\infty = 0.417(1)` は以前の結果（例えば、QMC による :math:`\Delta_\infty = 0.41048(6)` （Todo and Kato, PRL **87**, 047203 (2001)））とよくあっています。
