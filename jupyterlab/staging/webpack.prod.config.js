var UglifyJsPlugin = require('uglifyjs-webpack-plugin');
var merge = require('webpack-merge');
var common = require('./webpack.config');
const webpack = require('webpack');

const getPublicPath = () => {
  const branch = process.env.BUILD_GIT_BRANCH;
  if (branch) {
    const BUILD_GIT_GROUP = process.env.BUILD_GIT_GROUP;
    const BUILD_GIT_PROJECT = process.env.BUILD_GIT_PROJECT;

    if (/^daily/i.test(branch)) {
      return `//g.alicdn.daily.taobao.net/${BUILD_GIT_GROUP}/${BUILD_GIT_PROJECT}/`;
    } else if (/^publish/i.test(branch)) {
      return `//alinw.alicdn.com/${BUILD_GIT_GROUP}/${BUILD_GIT_PROJECT}/`;
    }
  }
  return '/';
};
common.plugins.unshift(
  new webpack.DefinePlugin({
    'process.env.DEV_MODE': false,
    'process.env.themePath': JSON.stringify(getPublicPath() + 'static/'),
    'process.env.publicPath': JSON.stringify(getPublicPath())
  })
);
module.exports = merge({
  customizeArray: merge.unique(
    'plugins',
    ['DefinePlugin'],
    plugin => plugin.constructor && plugin.constructor.name
  )
})(common, {
  mode: 'production',
  devtool: 'source-map',
  output: {
    publicPath: getPublicPath()
  },
  optimization: {
    minimizer: [
      new UglifyJsPlugin({
        parallel: true,
        sourceMap: false,
        uglifyOptions: {
          beautify: false,
          comments: false,
          compress: false,
          ecma: 6,
          mangle: true
        },
        cache: process.platform !== 'win32'
      })
    ]
  }
});
