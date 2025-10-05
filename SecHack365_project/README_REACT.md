# 患者情報共有システム - React版

医療従事者と患者の間で安全に医療情報を共有するためのReact Webアプリケーションです。

## 🚀 新機能（React版）

### モダンなアーキテクチャ
- **React 18** + **TypeScript** で型安全な開発
- **Zustand** でシンプルな状態管理
- **React Query** で効率的なAPI通信
- **Webpack** で最適化されたバンドル

### 改善された開発体験
- ホットリロード対応の開発サーバー
- TypeScript型チェック
- コンポーネントベースの設計
- 再利用可能なUI部品

## 📁 プロジェクト構成

```
SecHack365_project/
├── src/
│   ├── components/          # 再利用可能なコンポーネント
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── TagSelector.tsx
│   │   ├── MedicationCombination.tsx
│   │   ├── PatientSelectionModal.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── ErrorMessage.tsx
│   ├── pages/              # ページコンポーネント
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── InputFormPage.tsx
│   │   └── PatientDisplayPage.tsx
│   ├── store/              # 状態管理
│   │   └── useAppStore.ts
│   ├── api/                # API通信
│   │   └── client.ts
│   ├── types/              # TypeScript型定義
│   │   └── index.ts
│   ├── App.tsx
│   ├── index.tsx
│   └── index.css
├── package.json
├── webpack.config.js
├── tsconfig.json
└── .babelrc
```

## 🛠️ セットアップ

### 前提条件
- Node.js 16以上
- npm または yarn

### インストール

```bash
# 依存関係のインストール
npm install

# 開発サーバー起動
npm run dev

# 本番ビルド
npm run build
```

### アクセス
- **既存Flask API**: http://localhost:5001
- **模擬電子カルテ**: http://localhost:5002


## 🎯 主要機能

### 1. 認証システム
- パスワード認証
- WebAuthn（FIDO2）対応
- セッション管理

### 2. 患者管理
- 患者一覧表示
- 患者選択モーダル
- 患者データの取得・表示

### 3. 医療記録入力
- 症状タグ選択（カテゴリー別）
- 診断・処方薬管理
- 患者向け説明文生成
- リアルタイムプレビュー

### 4. データ連携
- 模擬電子カルテとの連携
- FHIR/CSV対応
- リアルタイム患者表示

## 🔧 開発

### コンポーネント設計
```tsx
// 例: Buttonコンポーネント
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'success' | 'danger';
  size?: 'small' | 'medium' | 'large';
  style?: React.CSSProperties;
}

const Button: React.FC<ButtonProps> = ({ ... }) => {
  // 実装
};
```

### 状態管理
```tsx
// Zustandストア
interface AppStore {
  user: User | null;
  currentPatient: Patient | null;
  selectedTags: Tag[];
  formData: FormData;
  // アクション
  setUser: (user: User | null) => void;
  updateFormField: (field: keyof FormData, value: string) => void;
}

export const useAppStore = create<AppStore>((set) => ({
  // 実装
}));
```

### API通信
```tsx
// React Query使用例
const { data: patients, isLoading } = useQuery({
  queryKey: ['patients'],
  queryFn: () => api.getPatients(),
});
```

## 🎨 スタイリング

### CSS設計
- グローバルスタイル（`index.css`）
- コンポーネント固有スタイル
- レスポンシブデザイン対応

### 主要クラス
```css
.btn { /* ボタンベーススタイル */ }
.btn-primary { /* プライマリボタン */ }
.form-control { /* フォーム要素 */ }
.card { /* カードコンテナ */ }
.tag { /* タグ要素 */ }
```

## 🚀 デプロイ

### 本番ビルド
```bash
npm run build
```

### 出力ファイル
- `dist/bundle.js` - メインJavaScriptファイル
- `dist/index.html` - HTMLテンプレート

## 🔄 既存システムとの比較

| 機能 | Vanilla JS版 | React版 |
|------|-------------|---------|
| 開発効率 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 保守性 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 型安全性 | ❌ | ✅ |
| コンポーネント化 | ❌ | ✅ |
| 状態管理 | 手動 | Zustand |
| API通信 | fetch | React Query |
| ホットリロード | ❌ | ✅ |

## 🐛 トラブルシューティング

### よくある問題

1. **TypeScriptエラー**
   ```bash
   # 型チェック実行
   npx tsc --noEmit
   ```

2. **依存関係エラー**
   ```bash
   # キャッシュクリア
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **開発サーバーエラー**
   ```bash
   # ポート変更
   npm run dev -- --port 3001
   ```

## 📚 参考資料

- [React公式ドキュメント](https://reactjs.org/)
- [TypeScript公式ドキュメント](https://www.typescriptlang.org/)
- [Zustand公式ドキュメント](https://zustand-demo.pmnd.rs/)
- [React Query公式ドキュメント](https://tanstack.com/query/latest)

## 🤝 貢献

プルリクエストやイシューの報告を歓迎します。

---

**詳細な技術仕様については [../README.md](../README.md) を参照してください。**
