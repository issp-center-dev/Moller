DSQSS による *moller* 計算の例
---------------------------------------------

このチュートリアルについて
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

これは、量子多体問題の経路積分モンテカルロ法を実行するためのオープンソースソフトウェアパッケージである `DSQSS <https://github.com/issp-center-dev/DSQSS>`__ を用いた ``moller`` の例です。この例では、周期境界条件下の :math:`S=1/2` (DSQSSの用語では:math:`M=1`) および :math:`S=1` (:math:`M=2`) 反強磁性ハイゼンベルク鎖の磁気感受率 :math:`\chi` の温度依存性を計算します。 ``moller`` を使用することで、異なるパラメーター (:math:`M, L, T`) の計算を並列に実行します。

この例は `公式チュートリアルの一つ <https://issp-center-dev.github.io/dsqss/manual/develop/en/dla/tutorial/spinchain.html>`__ に対応しています。

準備
~~~~~

``moller`` （HTP-tools）パッケージと ``DSQSS`` がインストールされていることを確認してください。このチュートリアルでは、ISSP のスーパーコンピュータシステム ``ohtaka`` を使用して計算を実行します。

実行方法
~~~~~~~~

1. データセットを準備する

   このパッケージに含まれるスクリプト ``make_inputs.sh`` を実行します。

   .. code:: bash

      $ bash ./make_inputs.sh

   これにより、 ``output`` ディレクトリが作成されます（すでに存在する場合は、まず削除し、再度作成します）。 ``output`` の下には、各パラメーター用の作業ディレクトリ（例： ``L_8__M_1__T_1.0``）が生成されます。ディレクトリのリストは ``list.dat`` ファイルに書き込まれます。

2. ``moller`` を使用してジョブスクリプトを生成する

   ジョブ記述ファイルを使用してジョブスクリプトを生成し、 ``job.sh`` というファイル名で保存します。

   .. code:: bash

      $ moller -o job.sh input.yaml

   次に、``job.sh`` を ``output`` ディレクトリにコピーし、 ``output`` ディレクトリに移動します。

3. バッチジョブを実行する

   ジョブリストを引数としてバッチジョブを送信します。

   .. code:: bash

      $ sbatch job.sh list.dat

4. 状態を確認する

   タスク実行の状態は ``moller_status`` プログラムによってまとめられます。

   .. code:: bash

      $ moller_status input.yaml list.dat

5. 結果を集める

   計算が終了した後、結果を以下のようにして集めます。

   .. code:: bash

      $ python3 ../extract_result.py list.dat

   このスクリプトは、:math:`M`, :math:`L`, :math:`T`, :math:`\chi` の平均、および :math:`\chi` の標準誤差を含む 5 列のテキストファイル ``result.dat`` に結果を書き込みます。

   結果を視覚化するために、GNUPLOT ファイル ``plot_M1.plt`` および ``plot_M2.plt`` が利用可能です。

   .. code:: bash

      $ gnuplot --persist plot_M1.plt
      $ gnuplot --persist plot_M2.plt

   |S=1/2 の磁気感受率| |S=2 の磁気感受率|

   :math:`S=1/2` と :math:`S=1` AFH 鎖の主な違いは、励起ギャップが消失するか (:math:`S=1/2`)、残るか (:math:`S=1`) のどちらかです。
   これを反映して、非常に低温領域での磁気感受率は、有限になる (:math:`S=1/2`) か、消失する (:math:`S=1`) かのどちらかです。
   :math:`S=1/2` の場合には、有限サイズ効果によりスピンギャップが開き、そのため小さいチェーンの磁気感受率が低下します。

.. |S=1/2 の磁気感受率| image:: ../../../../images/tutorial_dsqss_M1.*
.. |S=2 の磁気感受率| image:: ../../../../images/tutorial_dsqss_M2.*
