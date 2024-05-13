'use strict';

var gulp = require('gulp'),
    watch = require('gulp-watch'),
    autoprefix = require('gulp-autoprefixer'),
    sass = require('gulp-sass'),
    minifyCSS = require('gulp-clean-css'),
    rename = require('gulp-rename'),
    concat = require('gulp-concat'),
    uglify = require('gulp-uglify'),
    browserSync = require("browser-sync"),
    reload = browserSync.reload


/* =====================================================
    STYLES
    ===================================================== */

gulp.task('style:build:themes', function () {
    return gulp.src('./scss/themes/**/*.scss')
        .pipe(sass())
        .pipe(autoprefix({
            browsers: ['last 30 versions', '> 1%', 'ie 8', 'ie 9'],
            cascade: true
        }))
        .pipe(minifyCSS())
        .pipe(rename('themes.min.css'))
        .pipe(gulp.dest('./css/'))
        .pipe(reload({stream: true}));
});

gulp.task('style:build', function () {
    return gulp.src(['./scss/style.scss'])
        .pipe(sass())
        .pipe(autoprefix({
            browsers: ['last 30 versions', '> 1%', 'ie 8', 'ie 9'],
            cascade: true
        }))
        .pipe(minifyCSS())
        .pipe(rename('styles.min.css'))
        .pipe(gulp.dest('./css/'))
        .pipe(reload({ stream: true }));
});

/* =====================================================
    BUILD TASK
    ===================================================== */

gulp.task('build', [
    'style:build',
    'style:build:themes',
]);


/* =====================================================
    WATCH
    ===================================================== */

gulp.task('watch', function(){
    watch('./scss/**/*.scss', function(event, cb) {
        gulp.start('style:build');
    });
    watch(['./scss/themes/**/*.scss'], function(event, cb) {
        gulp.start('style:build:themes');
    });
});



/* =====================================================
    DEFAULT TASK
    ===================================================== */

gulp.task('default', ['build', 'watch']);