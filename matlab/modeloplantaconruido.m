sys=tf([2],[1 3 1])
[y,t]=step(sys);
x=repmat(1,size(t));
y2=awgn(y,2);
plot(t,y2)
plot(t,y2)
y2=awgn(y,1);
plot(t,y2)
y2=awgn(y,0.2);
plot(t,y2)
y2=awgn(y,0.01);
plot(t,y2)
y2=awgn(y,0.01,'measured');
plot(t,y2)
plot(t,y2)
y2=awgn(y,1,'measured');
plot(t,y2)
y2=awgn(y,10,'measured');
plot(t,y2)
y2=awgn(y,100,'measured');
plot(t,y2)
y2=awgn(y,20,'measured');
plot(t,y2)
y2=awgn(y,30,'measured');
plot(t,y2)
y2=awgn(y,40,'measured');
plot(t,y2)
data2=iddata(y2,x,0.0351)
sys3=tfest(data2,2)
step(sys)
hold on
step(sys3)
plot(t,y2)
step(sys)
hold on
step(sys3)
plot(t,y2)
plot(t,y2)
