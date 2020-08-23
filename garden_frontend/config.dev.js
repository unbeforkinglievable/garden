const path = require('path');

module.exports = {
    mode: 'development',
    entry: './src/index.js',
    output: {
        path: path.resolve(__dirname, 'build'),
        filename: 'bundle.js'
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /(node_modules|build|image)/,
                use: {
                    loader: 'babel-loader'
                }
            },
            {
                test: /\.html$/,
                exclude: /(node_modules|build|image)/,
                use: [
                    {
                        loader: 'html-loader'
                    }
                ]
            }
        ]
    },
    resolve: {
        extensions: ['*','.js','.jsx']
    }
};
