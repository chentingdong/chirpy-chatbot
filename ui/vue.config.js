
process.env.VUE_APP_ILLUSIONIST_PORT = process.env.ILLUSIONIST_PORT
process.env.VUE_APP_LUKE_URL = process.env.LUKE_URL

module.exports = {
  runtimeCompiler: true,

  // configureWebpack: config => {
  //   if (process.env.NODE_ENV === 'production') {
  //     // mutate config for production...
  //   } else {
  //     // mutate for development...
  //   }
  // }

  devServer: {
    host: '0.0.0.0',
    port: 2000
  },

  productionSourceMap: false,

  configureWebpack: {
    devtool: 'source-map'
  },

  css: {
    sourceMap: true,
    extract: false
  }
}
