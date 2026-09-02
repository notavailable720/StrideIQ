//
//  ContentView.swift
//  StrideIQ Watch App
//
//  Created by Tony Huang on 4/16/26.
//

// ContentView.swift
import SwiftUI

struct ContentView: View {
    @StateObject private var hr = HeartRateManager()
    
    var body: some View {
        VStack(spacing: 12) {
            Text("\(Int(hr.currentHR)) bpm")
                .font(.system(size: 44, weight: .bold, design: .rounded))
            Button(hr.isStreaming ? "Stop" : "Start") {
                if hr.isStreaming { hr.stop() }
                else { try? hr.start() }
            }
        }
        .task {
            try? await hr.requestAuth()
        }
    }
}
