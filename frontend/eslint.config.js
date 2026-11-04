import pluginVue from 'eslint-plugin-vue'
import tseslint from 'typescript-eslint'
import prettier from 'eslint-config-prettier'

export default [
  {
    // 通用错误规则：默认禁止不可达代码、重复参数和未定义的 JS 标识符。
    rules: {
      'no-unreachable': 'error',
      'no-dupe-args': 'error',
    },
  },
  {
    ignores: ['**/node_modules/**', '**/dist/**', '**/coverage/**', '**/.cache/**'],
  },
  ...tseslint.configs.recommended.map((config) => ({
    ...config,
    files: ['**/*.{ts,vue}'],
  })),
  ...pluginVue.configs['flat/recommended'],
  {
    files: ['**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: tseslint.parser,
        extraFileExtensions: ['.vue'],
        sourceType: 'module',
      },
    },
  },
  {
    files: ['**/*.{ts,vue}'],
    rules: {
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': 'error',
    },
  },
  {
    files: ['**/*.{js,mjs,cjs}'],
    rules: {
      'no-unused-vars': 'error',
      'no-undef': 'error',
    },
  },
  // 放在最后，关闭与 Prettier 冲突的格式规则。
  prettier,
]
