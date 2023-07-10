# Blue Moon Music Group App
## Background Information
Blue Moon Music Group is a non-profit organization based in Skillman, NJ, USA as part of Montgomery High School. Its goal is to provide quality, low-cost music education to all. Skilled high school student-musicians volunteer their time to teach lessons in the local community, the proceeds from which are donated to fund music education in underpriviliged communities. The organization offers lessons in over a dozen instruments to 100+ students taught by 50+ instructors. 

## Problem Statement
- Blue Moon lacks a proper website that conveys information about the organization to prospective student and instructors, donors, etc.
- The current student onboarding process is inefficient requiring a minimum of 4 emails sent back and forth and 1 week of processing time
- To match a student to an instructor, an administrator must manually sort through a complicated and long spreadsheet (on google sheets)

To address these issues, I built a web app using the Flask Python web framework along with HTML, CSS and Javascript. I used the google sheets api to maintain compatability with the current system to use as a database. There is a form on the site for prospective students and instructors to fill out and emails are sent automatically after the matching process with the spreadsheet is completed by a bot.

The website also clearly conveys information to visitors about the organization's goals and initiatives.

These changes decreased the processing time from 1 week to less than a minute.
