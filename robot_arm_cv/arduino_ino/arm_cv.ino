/*
 * rosserial PubSub Example
 * Prints "hello world!" and toggles led
 */

#include <ros.h>
#include <Servo.h>
#include <geometry_msgs/Quaternion.h>


class motor
{
  public:
  Servo s;
  void pin(int pin)
  {
    s.attach(pin);
  }

  void move1(int angle)
  {
    if(s.read() > angle)
    {
       for(int i=s.read();i>=angle;i--)
       {
          s.write(i);
          delay(20);
        }  
    }
    else if(s.read()<angle)
    {
      for(int i=s.read();i<=angle;i++)
      {
        s.write(i);
        delay(20);
      }  
    }  
  }

  
}shoulder,elbow,base,claw;

ros::NodeHandle  nh;


int sh=90,ba=90,cl=90,el=90;

void messageCb( const geometry_msgs::Quaternion& msg){
     ba=msg.x;
     sh=msg.y;
     el=msg.z;
     if (msg.w==1)
     {
      cl=20;
     }
     else
     {cl=90;}
     
}

ros::Subscriber<geometry_msgs::Quaternion> sub("/arm_angles", messageCb );


void setup()
{
   nh.getHardware()->setBaud(115200);
   nh.initNode();
   nh.subscribe(sub);
   shoulder.pin(5);
   elbow.pin(4);
   base.pin(3);
   claw.pin(7);
   shoulder.move1(90);
   elbow.move1(90);
   base.move1(90);
   claw.move1(90);
}

void loop()
{
  base.move1(ba);
  shoulder.move1(sh);
  elbow.move1(el);
  claw.move1(cl);
  nh.spinOnce();
  delay(1);
}
