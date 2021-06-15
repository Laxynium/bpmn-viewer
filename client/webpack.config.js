const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");

module.exports = {
  mode: "development",
  entry: {
    index: "./src/index.js",
  },
  devtool: "inline-source-map",
  plugins: [
    new HtmlWebpackPlugin({
      title: "Development",
      template: "src/index.html",
    }),
    new CopyWebpackPlugin([
      {
        from: "assets/**",
        to: "vendor/bpmn-js",
        context: "node_modules/bpmn-js/dist/",
      },
      { from: "**/*.{html,css}", context: "src/" },
      {
        from: "dict/**",
        to: "../server/static2",
        context: ".",
      },
    ]),
  ],
  output: {
    filename: "[name].bundle.js",
    path: path.resolve(__dirname, "dist"),
    clean: true,
  },
  module: {
    rules: [
      {
        test: /\.css$/i,
        use: ["style-loader", "css-loader"],
      },
    ],
  },
  devServer: {
    contentBase: "./dist",
    port: 9000,
  },
};
