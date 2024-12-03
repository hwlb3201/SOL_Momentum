import asyncio
import time
from constants import ABORT_ALL_POSITIONS, FIND_COINTEGRATED, PLACE_TRADES, MANAGE_EXITS
from func_connections import connect_dydx
from func_private import get_open_positions,is_open_positions, place_limit_order,Bid_ASK,cancel_order
from func_public import construct_market_prices,Momentum
import pandas as pd
from func_messaging import send_message

send_message("Bot launch successful")

async def bot():
  market='SOL-USD'
  size=0.01
  try:
    print("")
    print("Program started...")
    print("Connecting to Client...")
    client = await connect_dydx()
    print('connect successful')
    print()
  except Exception as e:
    print("Error connecting to client: ", e)
    send_message(f"Failed to connect to client {e}")
    exit(1)
  
    

  Is_position=await is_open_positions(client,market)

 
  if Is_position==True:
      print('There is position')
      position_inf=await get_open_positions(client,market)
      position_side=position_inf[0]
      entry_price=float(position_inf[1])  
      unrealizedPnl=float(position_inf[2])
      print(position_side)
      if position_side=="LONG":
           print(f"construct {market} price- Please wait......")
           candle=await construct_market_prices(client,market)
           Strategy=Momentum(candle,200)
           Strategy['Support']=0
           for current in range(1,len(Strategy)):
                previous=current-1
                if Strategy['Close'][current]>Strategy['Close'][previous]:
                      Strategy['Support'][current]=Strategy['Close'][current]
                else:
                      Strategy['Support'][current]=Strategy['Support'][previous]
            
           print(Strategy)
           if unrealizedPnl<=0:
                  Stop_price=entry_price*0.98
                  current_price=Strategy['Close'][-1]
                  if current_price<=Stop_price:
                        unrealizedPnl=float(position_inf[2])
                        orderbook=await Bid_ASK(client, market)
                        ask=float(orderbook[1])
                        side = "SELL"
                        await cancel_order(client,market)
                        await place_limit_order(client, market, side, size, ask, False)
                        send_message(f"Square the {position_side} {market} at {ask}, the unrealized is {unrealizedPnl}")
                  else: 
                      unrealizedPnl=float(position_inf[2])
                      send_message(f"The unrealized is {unrealizedPnl} and stop loss at {Stop_price}")
           else:
                
                Stop_price=Strategy['Support'][-1]*0.98
                current_price=Strategy['Close'][-1]
                if current_price<=Stop_price:
                        unrealizedPnl=float(position_inf[2])
                        orderbook=await Bid_ASK(client, market)
                        ask=float(orderbook[1])
                        side = "SELL"
                        await cancel_order(client,market)
                        await place_limit_order(client, market, side, size, ask, False)
                        send_message(f"Square the {position_side} {market} at {ask}, the unrealized is {unrealizedPnl}")
                else:
                        unrealizedPnl=float(position_inf[2])
                        send_message(f"The unrealized is {unrealizedPnl} and stop loss is at {Stop_price} ")       
      else:
            print(f"construct {market} price- Please wait......")
            candle=await construct_market_prices(client,market)
            Strategy=Momentum(candle,200)
            Strategy['Support']=0
            for current in range(1,len(Strategy)):
                previous=current-1
                if Strategy['Close'][current]<Strategy['Close'][previous]:
                      Strategy['Support'][current]=Strategy['Close'][current]
                else:
                      Strategy['Support'][current]=Strategy['Support'][previous]
            if unrealizedPnl<0:
                 Stop_price=entry_price*1.02
                 current_price=Strategy['Close'][-1]
                 if current_price>=Stop_price:
                      unrealizedPnl=float(position_inf[2])
                      orderbook=await Bid_ASK(client, market)
                      bid=float(orderbook[0])
                      side="BUY"
                      await cancel_order(client,market)
                      await place_limit_order(client, market, side, size, bid, False)
                      send_message(f"Square the {position_side} {market} at {bid}, the unrealized is {unrealizedPnl}")
                 else:
                      unrealizedPnl=float(position_inf[2])
                      send_message(f"The unrealized is {unrealizedPnl} and stop loss at {Stop_price}")
            else:
                  Stop_price=Strategy['Support'][-1]*1.02
                  current_price=Strategy['Close'][-1]
                  if current_price>=Stop_price:
                        unrealizedPnl=float(position_inf[2])
                        orderbook=await Bid_ASK(client, market)
                        bid=float(orderbook[0])
                        side= "BUY"
                        await cancel_order(client,market)
                        await place_limit_order(client, market, side, size, bid, False)
                        send_message(f"Square the {position_side} {market} at {bid}, the unrealized is {unrealizedPnl}")
                  else:
                        unrealizedPnl=float(position_inf[2])
                        send_message(f"The unrealized is {unrealizedPnl} and stop loss at {Stop_price}")                                                                                
  else:
      print('There is no position')
      print(f"construct {market} price- Please wait......")
      candle=await construct_market_prices(client,market)
      Strategy=Momentum(candle,200)
      print(Strategy)
      if Strategy['Close'][-1]>=Strategy['MA_200'][-1]:
            if Strategy['ret'][-1]>=0.015:
                  orderbook=await Bid_ASK(client, market)
                  bid=float(orderbook[0])
                  side="BUY"
                  await cancel_order(client,market)
                  await place_limit_order(client, market, side, size, bid, False)
                  send_message(f'Place a Buy order for {market} at {bid}')
            else: 
                 print(f'There is no signal for Long {market}')               
      elif Strategy['Close'][-1]<=Strategy['MA_200'][-1]:
            if Strategy['ret'][-1]<=-0.015:
                  orderbook=await Bid_ASK(client, market)
                  ask=float(orderbook[1])
                  side="SELL"
                  await cancel_order(client,market)
                  await place_limit_order(client, market, side, size, ask, False)
                  send_message(f'Place a Sell order for {market} at {ask}')
            else:
                  print(f'There is no signal for Short {market}')
      else:
            print(f'There is no signal for either long/Short {market}')
    

  time.sleep(600)




while True:
      try:
           asyncio.run(bot())
      except:
           print('+++++ MAYBE AN INTERNET PROB OR SOMETHING')


    
      
  
