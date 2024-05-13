// --------------------------------------------------
// [Gulpfile]
// --------------------------------------------------

'use strict';

var gulp 		= require('gulp'),
   sass 		= require('gulp-sass'),
   changed 	= require('gulp-changed'),
   cleanCSS 	= require('gulp-clean-css'),
   rename 		= require('gulp-rename'),
   uglify 		= require('gulp-uglify'),
   pump 		= require('pump');


// Gulp plumber error handler
function errorLog(error) {
   console.error.bind(error);
   this.emit('end');
}


// --------------------------------------------------
// [Libraries]
// --------------------------------------------------

// Sass - Compile Sass files into CSS
gulp.task('sass', function () {
   gulp.src('scss/**/*.scss')
       .pipe(changed('css/'))
       .pipe(sass({ outputStyle: 'expanded' }))
       .on('error', sass.logError)
       .pipe(gulp.dest('css/'));
});


// Minify CSS
gulp.task('minify-css', function() {
   // Theme
   gulp.src(['css/layout.css', 'css/layout.min.css'])
       .pipe(cleanCSS({debug: true}, function(details) {
           console.log(details.name + ': ' + details.stats.originalSize);
           console.log(details.name + ': ' + details.stats.minifiedSize);
       }))
       .pipe(rename({suffix: '.min'}))
       .pipe(gulp.dest('css/'));
});


// Minify JS - Minifies JS
gulp.task('uglify', function () {
    gulp.src(['main.js'])
        .pipe(uglify())
        .pipe(rename({ suffix: '.min' }))
        .pipe(gulp.dest('js/'));
});


// --------------------------------------------------
// [Gulp Task - Watch]
// --------------------------------------------------

// Lets us type "gulp" on the command line and run all of our tasks
gulp.task('default', ['sass', 'minify-css', 'uglify', 'watch']);

// This handles watching and running tasks
gulp.task('watch', function () {
   gulp.watch('scss/**/*.scss', ['sass']);
   gulp.watch('css/layout.css', ['minify-css']);
   gulp.watch('js/**/*.js', ['uglify']);
});