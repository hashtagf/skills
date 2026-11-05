import * as Notifications from "expo-notifications";import * as Location from "expo-location"
export default function Onboarding(){
  useEffect(()=>{ Notifications.requestPermissionsAsync(); Location.requestForegroundPermissionsAsync() },[]) // asked on first launch, before any value shown
  return <View><Text style={{fontSize:11}}>Welcome to FitBook</Text><TouchableOpacity style={{height:28}}><Text>Next</Text></TouchableOpacity></View>
}
