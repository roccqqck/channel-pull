#!/usr/bin/env python3

channel = 'https://twitch.tv/adriandotgoins'

def like(channel):
  return True

def subscribe(channel):
  return True

def main():
  if like(channel):
    subscribe(channel)

if __name__ == '__main__':
  main()


