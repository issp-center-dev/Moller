****************************************************************
概要
****************************************************************

mollerとは?
----------------------------------------------------------------

近年、機械学習を活用した物性予測や物質設計(マテリアルズインフォマティクス)が注目されています。
機械学習の精度は、適切な教師データの準備に大きく依存しています。
そのため、迅速に教師データを生成するためのツールや環境の整備は、
マテリアルズインフォマティクスの研究進展に大きく貢献すると期待されます。

mollerは、ハイスループット計算を支援するためのパッケージHTP-Toolsの一つとして提供しています。
mollerではスーパーコンピュータやクラスタ向けにバッチジョブスクリプトを生成するツールであり、
多重実行の機能を利用し、パラメータ並列など一連の計算条件について並列にプログラムを実行することができます。
現状では、東京大学 物性研究所の提供するスーパーコンピュータ ohtaka (slurmジョブスケジューラ) と kugui (PBSジョブスケジューラ) に加え、汎用のPBS系クラスタや、ジョブスケジューラを使用しないワークステーション等がサポートされています。

ライセンス
----------------------------------------------------------------

本ソフトウェアのプログラムパッケージおよびソースコード一式はGNU General Public License version 3 またはそれ以降のバージョン (GPL-3.0-or-later) に準じて配布されています。

開発貢献者
----------------------------------------------------------------

本ソフトウェアは以下の開発貢献者により開発されています。

-  ver.1.0.1 (2024/09/10リリース)

-  ver.1.0.0 (2024/03/06リリース)

-  ver.1.0-beta (2023/12/28リリース)

   -  開発者

      -  吉見 一慶 (東京大学 物性研究所)

      -  青山 龍美 (東京大学 物性研究所)

      -  本山 裕一 (東京大学 物性研究所)

      -  福田 将大 (東京大学 物性研究所)

      -  井戸 康太 (東京大学 物性研究所)

      -  福島 鉄也 (産業技術総合研究所)

      -  笠松 秀輔 (山形大学 学術研究院(理学部主担当))

      -  是常 隆　 (東北大学大学院理学研究科)

   -  プロジェクトコーディネーター

      -  尾崎 泰助 (東京大学 物性研究所)


コピーライト
----------------------------------------------------------------

.. only:: html

  |copy| *2023- The University of Tokyo. All rights reserved.*

  .. |copy| unicode:: 0xA9 .. copyright sign

.. only:: latex

  :math:`\copyright` *2023- The University of Tokyo. All rights reserved.*

本ソフトウェアは2023年度 東京大学物性研究所 ソフトウェア高度化プロジェクトの支援を受け開発されており、その著作権は東京大学が所持しています。

また、Miyabi および玄界へのインストール作業は、JST ムーンショット型研究開発事業 (グラント番号 JPMJMS24A3) の支援を受けたものです。

引用について
----------------------------------------------------------------

本ソフトウェアを利用した成果を発表する際には、以下の文献を引用していただけると幸いです。

  Kazuyoshi Yoshimi, Yuichi Motoyama, Tatsumi Aoyama, Mitsuaki Kawamura, and Naoki Kawashima,
  "Project for advancement of software usability in materials science",
  Science and Technology of Advanced Materials: Methods **5**, 2564055 (2025).
  `https://doi.org/10.1080/27660400.2025.2564055 <https://doi.org/10.1080/27660400.2025.2564055>`_

BibTeX形式:

.. code-block:: bibtex

  @article{Yoshimi2025,
    author  = {Kazuyoshi Yoshimi and Yuichi Motoyama and Tatsumi Aoyama and Mitsuaki Kawamura and Naoki Kawashima},
    title   = {Project for advancement of software usability in materials science},
    journal = {Science and Technology of Advanced Materials: Methods},
    volume  = {5},
    number  = {1},
    pages   = {2564055},
    year    = {2025},
    doi     = {10.1080/27660400.2025.2564055},
    url     = {https://doi.org/10.1080/27660400.2025.2564055}
  }

動作環境
----------------------------------------------------------------

以下の環境で動作することを確認しています。

- Ubuntu Linux + python3

また、以下のスーパーコンピュータで moller を利用できます。
各システム上での具体的な利用方法については、各システムの利用手引き等をご確認ください。

.. list-table::
   :header-rows: 1
   :widths: 20 50 30

   * - システム
     - 運用機関
     - 状況
   * - ohtaka, kugui
     - `物性研究所スーパーコンピュータセンター <https://mdcl.issp.u-tokyo.ac.jp/scc/>`_ (東京大学)
     - プリインストール済み
   * - `AOBA <https://www.ss.cc.tohoku.ac.jp/>`_
     - 東北大学 サイバーサイエンスセンター
     - プリインストール済み
   * - `玄界 <https://www.cc.kyushu-u.ac.jp/scp/system/genkai/>`_
     - 九州大学 情報基盤研究開発センター
     - プリインストール済み
   * - `Miyabi <https://www.cc.u-tokyo.ac.jp/supercomputer/miyabi/service/>`_
     - 東京大学 情報基盤センター
     - 対応済み (プリインストールは対応中, 2026/8/14現在)

